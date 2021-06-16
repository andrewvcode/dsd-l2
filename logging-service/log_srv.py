from flask import Flask, request, redirect
import hazelcast
import sys
app = Flask(__name__)


@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        getlogs = request.json
        print(getlogs)
        key = next(iter(getlogs.keys()))
        distributed_map.set(key,getlogs[key])
        return ''
    else:
        alllogs = '</br>'.join(distributed_map.get_all(distributed_map.key_set().result()).result().values())
        return alllogs

if __name__ == '__main__':
  
    client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        "172.17.0.4:5701",
        "172.17.0.5:5701",
        "172.17.0.6:5701",
    ],
    lifecycle_listeners=[
        lambda state: print("Lifecycle event >>>", state),
    ]
    )
    distributed_map = client.get_map("logs")
    app.run(port=int(sys.argv[1]), debug=True)
