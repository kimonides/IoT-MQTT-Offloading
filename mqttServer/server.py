import paho.mqtt.client as mqtt
import subprocess
import Queue as queue
#import queue
import signal, os,sys
import threading
import logging
import time
import datetime
import multiprocessing

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

AVERAGE_PROGRAM_RUNTIME = 1

def handler(signum, frame):
    client.loop_stop()
    time.sleep(1)
    logging.debug('Exiting with keyboard interrupt')
    sys.exit(0)

# This function gets called whenever we get a message to the inputCode/# topic
def codeProcess(client,userdata,message):
    # Process the device's request
    # This is the code offloading implementation
    # It takes the source code, compiles it and adds the path to the executable + the input arguments into the queue
    # for a thread to service it
    payload = message.payload.split('----')
    fileName = payload[0]
    codeArgs = payload[1]
    code = payload[2]
    makefile = payload[3]
    makefile = makefile.replace('<name>','./code/'+fileName).split(' ')

    f = open('./code/'+fileName+'.c','w+')
    f.write(code)
    f.close()
    subprocess.call(makefile)

    command = ('./code/'+fileName+' '+codeArgs).split(' ')
    Q.put( [ command , message.topic ] )
    # Create thread if possible and needed
    createThreads()
    return

# This function gets called whenever we get a message to the local/# topic
def inputProcess(client,userdata,message):
    # Adds to the queue the path to the executable + the input arguments so a thread can later service it
    command = './code/program '+message.payload
    command = command.split(' ')
    Q.put( [ command , message.topic ] )
    # Create thread if possible and needed
    createThreads()
    return

# This is our thread process it will run until the queue is empty and then it will terminate
def thread():
    while(runCode()):
        pass
    return

# This is the code services the requests in the queue
# It gets the path to the executable and the input arguments
# It executes the executable, if it was an offloaded code it deletes it and then it publishes the resulsts to the 
# localCode/<clientID> topic or the inputCode/<clientID> topic respectively
def runCode():
    try:
        logging.debug('Started')
        [command,inputTopic] = Q.get(timeout=1)
        topic = 'result/' + inputTopic.split('/')[1]
        output = subprocess.call(command)
        logging.debug('Publishing to '+topic)
        client.publish(topic,output)
        print(command[0])
        if(command[0] != './code/program'):
            os.remove(command[0])
            os.remove(command[0]+'.c')
        logging.debug('Finished')
        return True
    except queue.Empty:
        logging.debug('Exiting')
        return False

# Create as many threads as possible that will process the messages in the queue
# It tops at number of cores-1 , because 1 thread will keep listening on the 1883 port for messages
# and having more threads then the number of cores owrking simultaneously won't be efficient
def createThreads():
    workload = Q.qsize()
    activeThreads = threading.active_count()

    if(workload>=2 and activeThreads<4):
        maxEfficientThreadNumber = 4 - activeThreads
        maxThreadNumber = workload - activeThreads

        newThreads = min(maxEfficientThreadNumber,maxThreadNumber)

        # Create threads that run the code in the function called thread
        for _ in range(newThreads):
            t = threading.Thread(target=thread)
            t.setDaemon(True)
            t.start()
    

# Set a signal handler for the SIGINT signal
signal.signal(signal.SIGINT, handler)

#Start the mqtt client on localhost port 1883
client = mqtt.Client(clean_session=True)
client.connect("localhost",port=1883)

# Set the handlers for each topic
client.message_callback_add('localCode/#', inputProcess)
client.message_callback_add('inputCode/#', codeProcess)

# Initialize a synchronized queue
Q = queue.Queue()

# Start listening
client.loop_start()

# Subscribe to the inputCode/# and localCode/# topics , # stands for anything
time.sleep(1)
client.subscribe("inputCode/#")
client.subscribe("localCode/#")

while True:
    if(Q.qsize()>0): 
        runCode()

    












