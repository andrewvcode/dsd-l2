import uuid
import requests
from flask import Flask, request, redirect

app = Flask(__name__)


@app.route('/')
def redirect_root():
    return redirect("/fascad_service", code=302)

@app.route('/fascad_service', methods=['GET', 'POST'])
def fascade():
    if request.method == 'POST':

        if request.json.get('msg'):
            content = {str(uuid.uuid4()): request.json.get('msg')}
            requests.post('http://localhost:5002/log', json=content)
            return 'Request accepted'
        else:
            return 'Bad Request', 400
    else:      
        getlogs = requests.get('http://localhost:5002/log')
        answer = getlogs.content.decode("utf-8")
        return answer, 200   
if __name__ == '__main__':
    app.run(port=5001, debug=True)
