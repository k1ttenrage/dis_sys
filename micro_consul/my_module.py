from random import randint
from uuid import uuid4
from json import loads
from os import getenv
import consul

CONSUL_HOST = "127.0.0.1"
CONSUL_PORT = 8500
CONSUL_CLIENT = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

def register_service(service_name, service_port):
    service_id = str(uuid4())
    service_ip = getenv('SERVICE_IP', 'localhost')
    CONSUL_CLIENT.agent.service.register(
        service_name,
        service_id=service_id,
        address=service_ip,
        port=service_port
    )
    return service_id

def deregister_service(id):
    return CONSUL_CLIENT.agent.service.deregister(id)

def get_service_address(service_name):
    _, services = CONSUL_CLIENT.catalog.service(service_name)
    service = randint(0, len(services) - 1)
    if services:
        address = services[service]['ServiceAddress']
        port = services[service]['ServicePort']
        return f"http://{address}:{port}"
    else:
        raise Exception(f"Service '{service_name}' not found in Consul.")
    
def get_settings(setting):
    _, settings = CONSUL_CLIENT.kv.get(setting)
    if settings:
        return loads(settings['Value'])
    else:
        raise Exception("settings not found in Consul.")

def put_setting(setting, value):
    CONSUL_CLIENT.kv.put(setting, value)
