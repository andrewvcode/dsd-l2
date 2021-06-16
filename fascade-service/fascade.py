import uuid
import requests
from flask import Flask, request, redirect
import random

app = Flask(__name__)


@app.route('/')
def redirect_root():
    return redirect("/fascad_service", code=302)

@app.route('/fascad_service', methods=['GET', 'POST'])
def fascade():
    micro_logs_ports = [5005,5006,5007]
    ml_port = random.choice(micro_logs_ports)

    if request.method == 'POST':
        if request.json.get('msg'):
            content = {str(uuid.uuid4()): request.json.get('msg')}
            requests.post(f'http://localhost:{ml_port}/log', json=content)
            return 'Request accepted'
        else:
            return 'Bad Request', 400
    else:  
        getlogs = requests.get(f'http://localhost:{ml_port}/log')
        getmessages = requests.get('http://localhost:5003/')
        answer = '<div>' + '<h3>Logs:</h3>' + getlogs.content.decode("utf-8") + '</div>' + '<div>' + '<h3>Messages:</h3>' + getmessages.content.decode("utf-8") + '</div>'
        return answer, 200   

if __name__ == '__main__':
    app.run(port=5001, debug=True)
