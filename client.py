
#!/usr/bin/env python

#title           :client.py
#description     :Todo.
#author          :Group 8
#date            :15.01.2018
#version         :0.2
#usage           :python client.py
#notes           :
#python_version  :2.7.12 
#==============================================================================

# Import modules
import socket
import sys
import hashlib
import os
from threading import Thread
from time import sleep

# Constants
PORT = 5000
BUFFER_SIZE = 4096
slowSocketExists = False;
fastSocketExists = False;
buffer = 'Hello World\n'

def heartbeat(arg):
	while True:
		response = os.system("ping -c 1 " + arg)
		if response == 0:
        		print arg, " is up!"
			openSocket(arg, arg=='10.0.0.3')
			
		else:
			print arg, " is down!"
			closeSocket(arg, arg=='10.0.0.3')
		sleep(1)


hbthreadslow = Thread(target = heartbeat, args=('10.0.0.3', ))
hbthreadslow.start();
hbthreadfast = Thread(target = heartbeat, args=('10.1.0.3', ))
hbthreadfast.start();

#Open TCP/IP client socket
def openSocket(arg, slow):
	#find out if socket exists already
	if (slow):
		if (not slowSocketExists):
			slowSocketExists = True
			slowSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect the socket to the port where the server is listening
		try:
    			slowSocket.connect(arg, 5000)
			print('connecting to {} port {}'.format(*(arg,5000)))
		except socket.error , msg:
    			print('Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sendData(slowSocket)		
		#TODO start sending on slow socket
	else:
		if (not fastSocketExists):
			fastSocketExists = True
			fastSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
    			fastSocket.connect(arg, 5000)
			print('connecting to {} port {}'.format(*(arg,5000)))
		except socket.error , msg:
    			print('Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		#TODO start sending on fast socket

#Close TCP/IP client socket
def closeSocket(arg, slow):
	#find out if socket exists already
	if (slow):
		if (slowSocketExists):
			#TODO interrupt sending on slow socket
			slowSocketExists = False
	else:
		if (fastSocketExists):
			#TODO interrupt sending on fast socket
			fastSocketExists = True
	
	
def sendData(sendsocket):
	hasher = hashlib.sha256()
	with open('dummyfiles/dummy_large.jpeg', 'rb') as afile:
    		buf = afile.read()
    		hasher.update(buf)
		print(hasher.hexdigest())
 
	try:
   		sendsocket.sendall(buf)
	except socket.timeout:
   		print('Error socket timedout')

	client.close()

def set_keepalive(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

def set_keepalive_osx(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    sends a keepalive ping once every 3 seconds (interval_sec)
    """
    # scraped from /usr/include, not exported by python's socket module
    TCP_KEEPALIVE = 0x10
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)

#try:
    # Send data
#    message = b'Hello World!'
#    print('sending {!r}'.format(message))
#    s.sendall(message)
#finally:
#    print('closing socket')
#    s.close()
