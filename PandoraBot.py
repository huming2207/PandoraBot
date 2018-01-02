from flask import Flask, request, Response, redirect, send_file
from werkzeug.utils import secure_filename
from threading import Thread
import os, io

from ToolRunner import ToolRunner
from Settings import Settings

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/flashrom_status')
def get_flashrom_log():
    def read_flashrom_log():

        # Try load log files
        log_file = open(Settings.load_settings("flashrom_log_location"), "r")

        # Stream file to the client
        while True:
            new_line = log_file.readline()

            # Stream the file to the client until it ends. When it ends, remove it.
            if "PBT: Flashrom process finished!" in new_line:
                yield new_line.encode("utf-8")  # Flush the last line
                os.remove(Settings.load_settings("flashrom_log_location"))
                break

            yield new_line.encode("utf-8")

    return Response(read_flashrom_log(), mimetype="text/plain",
                    headers={"Content-Disposition": "inline; filename=flashrom.log"})


@app.route("/flashrom_file")
def get_flashrom_cache():
    with open(Settings.load_settings("flashrom_cache_location"), "rb") as cache_file:
        return send_file(io.BytesIO(cache_file.read()),
                         mimetype="application/octet-stream",
                         attachment_filename="flash_dump.bin")


# GET => Read, POST => Write, DELETE => Erase
@app.route('/flashrom', methods=["GET", "POST", "DELETE"])
def run_flashrom():
    if request.method == "GET":

        flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                 args=("read",
                                         Settings.load_settings("flashrom_cache_location"),
                                         Settings.load_settings("flashrom_programmer")))

        flashrom_thread.start()

    elif request.method == "DELETE":

        flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                 args=("erase", "", Settings.load_settings("flashrom_programmer")))

        flashrom_thread.start()

    elif request.method == "POST":

        flash_bin = request.files['file']
        flash_bin.save(os.path.join(Settings.load_settings("flashrom_upload_file_path"),
                                    secure_filename(flash_bin.filename)))

        flashrom_thread = Thread(target=ToolRunner.start_flashrom,
                                 args=("write", Settings.load_settings("flashrom_cache_location"),
                                        Settings.load_settings("flashrom_programmer")))

        flashrom_thread.start()

    return Response("OK", mimetype="text/plain", status=200)


if __name__ == '__main__':
    app.run(threaded=True)
