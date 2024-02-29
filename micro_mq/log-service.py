from flask import Flask, request
from subprocess import run
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

hz = hazelcast.HazelcastClient(cluster_name="lab4")

messages = hz.get_map("messages").blocking()

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
    run(['docker-compose', f'-flog_{hz_port}.yml', 'stop'])