# IoT-Project
## MQTT
The MQTT messaging protocol has been used for this project.  
I used Mosquitto as my MQTT broker, but any other broker is viable as long as
it supports broker generated clientIDs.  
To run with Mosquitto just install mosquitto and run it with the mosquitto.conf configuration file.  
## Server 

For this project the server was ran on an NVIDIA Jetson Nano that boasts increased AI performance.  
In this project's implementation the gateway acts as both the broker and a client that serves all the incoming requests.  
The server is subscribed to the localCode/# and inputCode/# topics.The hastag stands for any subtopic under the localCode 
topic and inputCode topic respectively.  
  
  
All the other clients publish at the localCode/<clientID> topic if they want to run code that is available on the server with input given by the client.  

A client can also publish at the inputCode/<clientID> topic if they want to offload code to the server to be run, in the published  
message the client sends it's clientID, the input arguments, the code to be compiled and executed and the makefile.  

All the incoming requests to the server are served by a handler thread that processes the request and inserts it into the 
request queue. If the request is an offload request the handler will create and compile the code and insert the path to the new executable
and the input arguments into the request queue.

The server uses multiple threads, spawning as many as effectively possible to match the demand. Each thread serves requests from the synchronized
request queue. The results are published at the result/<clientID> topic that all the other clients are subscribed to and waiting for their results.

## Client
For the project to be tested and ran I implemented an Arduino client that periodically sends requests to the server.
Two Linux clients that ran on Raspberry Pis, one for testing the offloading and one for testing simple local code requests.
The above mentioned clients all have been made just for testing by giving the same file for offloading and the same input all the time but
it can be changed to take a file given by the user to the offloaded and input given by the user.


