from flask import Flask, request
from subprocess import run
import my_module
import hazelcast
import argparse

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--hport", type=int, required=True)
parser.add_argument("--fport", type=int, required=True)
args = parser.parse_args()

hz_port = args.hport
flask_port = args.fport

run(['docker-compose', f'-flog_{hz_port}.yml', 'up', '-d'])

hz_settings = my_module.get_settings('hz_settings')
hz = hazelcast.HazelcastClient(cluster_name=hz_settings['cluster_name'])
service_id = my_module.register_service('logging-service', flask_port)
messages = hz.get_map(hz_settings['map_name']).blocking()

@app.route("/logging", methods=["POST", "GET"])
def log_request():
    array = {}
    array['messages_from_log'] = []
    if request.method == "POST":
        _id = request.form.get('id')
        _msg = request.form.get('msg')
        messages.put(_id, _msg)
        if not (_id or _msg):
            abort(400, "Missing 'id' or 'msg' field in the request")
        print("Received message:", _msg)
        return "Message logged successfully", 201
    elif request.method == "GET":
        keys = messages.key_set()
        for key in keys:
            array['messages_from_log'].append(messages.get(key))
        return array
    else:
        abort(400)

app.run(port=flask_port)

try:
    while True:
        pass
except KeyboardInterrupt:
    hz.shutdown()
    my_module.deregister_service(service_id)
    run(['docker-compose', f'-flog_{hz_port}.yml', 'stop'])