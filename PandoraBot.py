from flask import *
from werkzeug.utils import secure_filename
from threading import Thread
import os, io

from ToolRunner import ToolRunner
from Settings import Settings

app = Flask(__name__, template_folder="templates")


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/flashrom_log')
def get_flashrom_log():
    def read_flashrom_log():

        # Try load log files
        log_file = open(Settings.load_settings("flashrom_log_location"), "r")

        # Stream file to the client
        while True:
            new_line = log_file.readline()

            # Stream the file to the client until it ends. When it ends, remove it.
            if "PBT: Flashrom process finished!" in new_line:
                yield new_line  # Flush the last line
                os.remove(Settings.load_settings("flashrom_log_location"))
                break

            # Return the line only if the line is not empty
            if new_line:
                yield new_line + "<br>"

    return Response(stream_with_context(read_flashrom_log()))


@app.route("/flashrom.bin")
def get_flashrom_cache():
    with open(Settings.load_settings("flashrom_cache_location"), "rb") as cache_file:
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
                                             Settings.load_settings("flashrom_cache_location"),
                                             Settings.load_settings("flashrom_programmer")))

            flashrom_thread.start()

        elif request.args.get("flashrom-mode", default="") == "erase":

            flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                     args=("erase", "", Settings.load_settings("flashrom_programmer")))

            flashrom_thread.start()

    # Write (Flash) with POST
    elif request.method == "POST":

        flash_bin = request.files['rom']
        flash_bin.save(os.path.join(Settings.load_settings("flashrom_upload_file_path"),
                                    secure_filename(flash_bin.filename)))

        flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                 args=("write", Settings.load_settings("flashrom_cache_location"),
                                        Settings.load_settings("flashrom_programmer")))

        flashrom_thread.start()

    return render_template("flashrom_run.html",
                           flashrom_read=request.args.get("flashrom-mode", default="") == "read")


# Shorten caching timeout to 10 seconds
@app.after_request
def add_header(response):
    response.cache_control.max_age = 10
    return response


if __name__ == '__main__':
    app.run(threaded=True)
