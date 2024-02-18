import hazelcast

client = hazelcast.HazelcastClient(cluster_name="lab2")
queue = client.get_queue("queue").blocking() 

while True:
    item = queue.take()
    print("Consumed " + str(item))
    if (item == -1):
        queue.put(-1)
        break