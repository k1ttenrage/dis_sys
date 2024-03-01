from flask import Flask, request, abort, jsonify
from uuid import uuid4
import my_module
import hazelcast
from requests import get, post
from json import dumps
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

service_id = my_module.register_service('facade-service', args.port)
hz_settings = my_module.get_settings('hz_settings')
hz = hazelcast.HazelcastClient(cluster_name=hz_settings['cluster_name'])
queue = hz.get_queue(hz_settings['queue_name']).blocking()

app = Flask(__name__)
msgs = {}
msgs['messages_from_msg'] = []

@app.route("/", methods=["POST", "GET"])
def handle_request():

    log_service = f"{my_module.get_service_address('logging-service')}/logging"
    msg_service = f"{my_module.get_service_address('messages-service')}/messages"

    if request.method == "POST":
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid4())
        data = {"id": _id, "msg": _msg}
        response = post(log_service, data=data)
        queue.offer(dumps(_msg))
        return jsonify(data), 200
    
    elif request.method == "GET":
        log_response = get(log_service)
        msg_response = get(msg_service).json()
        print(msg_response['messages_from_msg'])
        for i in msg_response['messages_from_msg']: 
            if i not in msgs['messages_from_msg']:
                msgs['messages_from_msg'].append(i)
        return [log_response.text, msgs], 200
    
    else:
        abort(400)

app.run(port=args.port)

try:
    while True:
        pass
except KeyboardInterrupt:
    hz.shutdown()
    my_module.deregister_service(service_id)