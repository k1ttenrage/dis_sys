from flask import Flask
import hazelcast
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', "--port", type=int, required=True)
args = parser.parse_args()
port = args.port

app = Flask(__name__)

hz = hazelcast.HazelcastClient(cluster_name="lab4")
queue = hz.get_queue("queue").blocking()

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
            exit()

@app.route('/messages', methods=['GET'])
def get_messages():
    print(array)
    return array

if __name__ == '__main__':
    thread_one = threading.Thread(target=pool_queue)
    thread_one.start()
    app.run(port=port)