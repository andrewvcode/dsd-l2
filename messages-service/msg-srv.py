from flask import Flask

app = Flask(__name__)


@app.route('/')
def msg():
    return "Empty"

if __name__ == '__main__':
    app.run(port=5003, debug=True)
