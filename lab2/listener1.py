import hazelcast
import datetime

def on_message(event):
    print("Got message:", event.message)
    print("Publish time:", datetime.datetime.fromtimestamp(event.publish_time))

client = hazelcast.HazelcastClient(cluster_name="lab2")
topic = client.get_topic("my-distributed-topic").blocking()

topic.add_listener(on_message)

try:
    while True:
        pass
except KeyboardInterrupt: 
    client.shutdown()
    print("end of work")