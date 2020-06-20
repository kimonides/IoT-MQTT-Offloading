import paho.mqtt.client as mqtt
import sys,os,signal
import logging
import time

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


def on_message(client,userdata,message):
    print(  str( message.payload.decode('utf-8') )  )

def handler(signum, frame):
    logging.debug('Shutting down node with keyboard interrupt')
    client.loop_stop()
    sys.exit(0)


signal.signal(signal.SIGINT, handler)

client = mqtt.Client(clean_session=True)
client.connect("localhost",port=1883)
client.on_message = on_message


client.loop_start()

time.sleep(1)
client.subscribe("result/"+client._client_id)

with open("kappa.c",'r') as file:
    data = file.read()

input = '1 2'
makefile = "gcc <name>.c -o <name>"

message = client._client_id+"----"+input+"----"+data+"----"+makefile

client.publish('toProcessCode/'+client._client_id,message)
while True:
    pass

client.loop_stop()
    