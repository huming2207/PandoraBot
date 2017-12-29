from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/flashrom', methods=["GET", "POST"])
def run_flashrom():
    setting_req = request.args.get("mode")






if __name__ == '__main__':
    app.run()
