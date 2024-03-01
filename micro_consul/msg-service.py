from flask import Flask
import hazelcast
import argparse
import my_module
import threading

parser = argparse.ArgumentParser()
parser.add_argument('-p', "--port", type=int, required=True)
args = parser.parse_args()
port = args.port

app = Flask(__name__)
hz_settings = my_module.get_settings('hz_settings')
service_id = my_module.register_service('messages-service', port)
hz = hazelcast.HazelcastClient(cluster_name=hz_settings['cluster_name'])
queue = hz.get_queue(hz_settings['queue_name']).blocking()

array = {}
array['messages_from_msg'] = []

def pool_queue():
    while True:
        try:
            msg = queue.take()
            print(msg)
            array['messages_from_msg'].append(msg)
            if (msg == -1):
                queue.put(-1)
                break
        except:
            hz.shutdown()
            my_module.deregister_service(service_id)
            exit()

@app.route('/messages', methods=['GET'])
def get_messages():
    print(array)
    return array

thread_one = threading.Thread(target=pool_queue)
thread_one.start()

try:
    app.run(port=port)
    thread_one.join()
except KeyboardInterrupt:
    hz.shutdown()
    my_module.deregister_service(service_id)
    exit()