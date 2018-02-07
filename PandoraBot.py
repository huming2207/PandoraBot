from flask import *
from werkzeug.utils import secure_filename
from threading import Thread
import os, io, logging

from Gpio import Gpio
from ToolRunner import ToolRunner
from Settings import Settings
from LogHelpers import LogHelpers

app = Flask(__name__, template_folder="templates")
log_helper = LogHelpers()


@app.route('/')
def render_index():
    return render_template("index.html")


@app.route('/stream_flashrom_log')
def get_flashrom_log():
    return Response(
        stream_with_context(log_helper.stream_log(log_file=open(Settings.get("flashrom_log_location"), "r"),
                                                  delete=False, end_line="PBT: Flashrom process finished!")))


@app.route('/flashrom_progress')
def get_flashrom_status():
    return jsonify(progress=log_helper.flashrom_percentage,
                   addr_start=log_helper.flashrom_addr_start,
                   addr_end=log_helper.flashrom_addr_end)


@app.route('/stream_ocd_log')
def get_ocd_log():
    return Response(
        stream_with_context(log_helper.stream_log(log_file=open(Settings.get("flashrom_log_location"), "r"),
                                                  delete=False, end_line="PBT: OpenOCD process finished!")))


@app.route("/flashrom.bin")
def get_flashrom_cache():
    with open(Settings.get("flashrom_cache_location"), "rb") as cache_file:
        return send_file(io.BytesIO(cache_file.read()),
                         mimetype="application/octet-stream",
                         attachment_filename="flash_dump.bin")


# GET => Read/Erase, POST => Write
@app.route('/flashrom', methods=["GET", "POST"])
def run_flashrom():
    # Erase/Read with GET
    if request.method == "GET":

        if request.args.get("flashrom-mode", default="") == "read":

            flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                     args=("read",
                                           Settings.get("flashrom_cache_location"),
                                           Settings.get("flashrom_programmer")))

            flashrom_thread.start()

        elif request.args.get("flashrom-mode", default="") == "erase":

            flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                     args=("erase", "", Settings.get("flashrom_programmer")))

            flashrom_thread.start()

    # Write (Flash) with POST
    elif request.method == "POST":

        flash_bin = request.files['rom']
        flash_bin.save(os.path.join(Settings.get("flashrom_upload_file_path"),
                                    secure_filename(flash_bin.filename)))

        flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                 args=("write", Settings.get("flashrom_cache_location"),
                                       Settings.get("flashrom_programmer")))

        flashrom_thread.start()

    return render_template("flashrom_run.html",
                           flashrom_read=request.args.get("flashrom-mode", default="") == "read")


@app.route("/hardware", methods=["GET"])
def get_hardware_page():
    return render_template("hardware.html")


@app.route("/openocd", methods=["POST", "GET"])
def run_openocd():
    if request.method == "POST":

        file_list = []

        for ocd_config in request.files.getlist('config'):
            ocd_config.save(os.path.join(Settings.get("ocd_config_location"), secure_filename(ocd_config.filename)))
            file_list.append(os.path.join(Settings.get("ocd_config_location"), secure_filename(ocd_config.filename)))

        ocd_thread = Thread(target=ToolRunner.start_openocd, args=(file_list, True))
        ocd_thread.start()

        return render_template("ocd_run.html")

    elif request.method == "GET" and request.args.get("ocd-cmd", default="") == "kill":

        ToolRunner.kill_process("openocd")
        return jsonify(status="OK", message="OpenOCD has been terminated.")


@app.route("/uart", methods=["GET"])
def run_uart():
    if request.args.get("uart-cmd", default="") == "kill":
        ToolRunner.kill_process("ttyd")
        return jsonify(status="OK", message="ttyd has been terminated.")
    else:
        data = str(request.args.get("data", default=""))
        parity = str(request.args.get("parity", default=""))
        flow = str(request.args.get("flow", default=""))
        baud = str(request.args.get("baud", default=""))

        # If any of these parameters contain some illegal chars (e.g. '&' and ';'), it should be intercepted.
        if not data.isalnum() or not parity.isalnum() or not flow.isalnum() or not baud.isalnum():
            return jsonify(status="PARAM_ERR", message="Parameter is corrupted")

        # Start the thread
        ttyd_thread = Thread(target=ToolRunner.start_ttyd, args=(baud, data, flow, parity))
        ttyd_thread.start()

        return jsonify(status="OK", message="OK")


@app.route("/gpio_out", methods=["GET"])
def handle_gpio_out():

    # Pin selection
    if not str(request.args.get("pin", default="")).isdigit():
        return jsonify(status="PARAM_ERR", message="Bad Request, pin argument is not even a number")

    selected_pin = int(request.args.get("pin"))

    # FIXME: use regexp later
    # Selected pin must be 0, 14-17 (used by soft SPI), 39 to 42, or it should return 400 to block this request
    if not selected_pin == 0 and not 39 <= selected_pin <= 42:
        return jsonify(status="PARAM_ERR", message="Bad Request: not a valid pin number")

    # Value selection
    if not str(request.args.get("value")).isdigit():
        return jsonify(status="PARAM_ERR", message="Bad Request: value selection incorrect")

    value = int(request.args.get("value", default="-1"))

    # If all good, then...
    gpio = Gpio(selected_pin, app)

    if not gpio.set_mode("out"):
        return jsonify(status="INTERNAL_ERR", message="Internal Error: set mode failed, check dmesg log please")

    if not gpio.set_value(value):
        return jsonify(status="INTERNAL_ERR", message="Internal Error: set value failed, check dmesg log please")

    return jsonify(status="OK", message="OK")


@app.route("/gpio_in", methods=["GET"])
def handle_gpio_in():
    # Pin selection
    if not str(request.args.get("pin", default="")).isdigit():
        return jsonify(status="PARAM_ERR", message="Bad Request, pin argument is not even a number")

    selected_pin = int(request.args.get("pin"))

    # FIXME: use regexp later
    # Selected pin must be 0, 14-17 (used by soft SPI), 39 to 42, or it should return 400 to block this request
    if not selected_pin == 0 and not 39 <= selected_pin <= 42:
        return jsonify(status="PARAM_ERR", message="Bad Request: not a valid pin number")

    # If all good, then...
    gpio = Gpio(selected_pin, app)

    if not gpio.set_mode("in"):
        return jsonify(status="INTERNAL_ERR", message="Internal Error: set mode failed, check dmesg log please")

    gpio_value = gpio.get_value()

    if gpio_value == -1:
        return jsonify(status="INTERNAL_ERR", message="Internal Error: cannot read GPIO value")
    else:
        return jsonify(status="OK", message=str(gpio_value))


# Shorten caching timeout to 10 seconds
@app.after_request
def add_header(response):
    response.cache_control.max_age = 10
    return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0")
