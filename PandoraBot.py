from flask import *
from werkzeug.utils import secure_filename
from threading import Thread
import os, io

from ToolRunner import ToolRunner
from Settings import Settings

app = Flask(__name__, template_folder="templates")


def read_log(log_file_path, delete=False, end_line="process finished"):
    # Try load log files
    log_file = open(log_file_path, "r")

    # Stream file to the client
    while True:
        new_line = log_file.readline()

        # Stream the file to the client until it ends. When it ends, remove it.
        if end_line in new_line:
            yield new_line  # Flush the last line

            if delete:
                os.remove(log_file_path)

            break

        # Return the line only if the line is not empty
        if new_line:
            yield new_line + "<br>"


@app.route('/')
def render_index():
    return render_template("index.html")


@app.route('/flashrom_log')
def get_flashrom_log():
    return Response(
        stream_with_context(read_log(Settings.get("flashrom_log_location"),
                                     delete=True, end_line="PBT: Flashrom process finished!")))


@app.route('/ocd_log')
def get_ocd_log():
    return Response(
        stream_with_context(read_log(Settings.get("ocd_log_location"),
                                     delete=True, end_line="PBT: OpenOCD process finished!")))


@app.route("/flashrom.bin")
def get_flashrom_cache():
    with open(Settings.get("flashrom_cache_location"), "rb") as cache_file:
        return send_file(io.BytesIO(cache_file.read()),
                         mimetype="application/octet-stream",
                         attachment_filename="flash_dump.bin")


# GET => Read, POST => Write
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


@app.route("/openocd", methods=["POST"])
def run_openocd():

    print(request.files["config"])

    file_list = []

    for ocd_config in request.files.getlist('config'):
        ocd_config.save(os.path.join(Settings.get("ocd_config_location"), secure_filename(ocd_config.filename)))
        file_list.append(os.path.join(Settings.get("ocd_config_location"), secure_filename(ocd_config.filename)))

    ocd_thread = Thread(target=ToolRunner.start_openocd, args=(file_list, True))

    ocd_thread.start()

    return render_template("ocd_run.html")


# Shorten caching timeout to 10 seconds
@app.after_request
def add_header(response):
    response.cache_control.max_age = 10
    return response


if __name__ == '__main__':
    app.run(threaded=True)
