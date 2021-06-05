from flask import Flask, request, redirect

app = Flask(__name__)


@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        logs.update(request.json)
        print(request.json)
        return ''
    else:
        return ','.join(logs.values())

if __name__ == '__main__':
    logs = {}
    app.run(port=5002, debug=True)
