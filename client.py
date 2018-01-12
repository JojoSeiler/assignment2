
#!/usr/bin/env python

#title           :client.py
#description     :Todo.
#author          :Group 8
#date            :13.12.2017
#version         :0.1
#usage           :python client.py
#notes           :
#python_version  :2.7.12 
#==============================================================================

# Import modules
import socket
import sys
import hashlib

# Constants
HOST = 'localhost'
PORT = 5000
ADDR = (HOST,PORT)
BUFFER_SIZE = 4096

buffer = 'Hello World\n'

hasher = hashlib.sha256()
with open('dummyfiles/512K_dummy.txt', 'rb') as afile:
    buf = afile.read()
    hasher.update(buf)
print(hasher.hexdigest())
 
# Create TCP/IP client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('socket created')
 
# Connect the socket to the port where the server is listening
try:
    client.connect(ADDR)
    print('connecting to {} port {}'.format(*ADDR))
except socket.error , msg:
    print('Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

client.sendall(buf)

client.close()

#try:
    # Send data
#    message = b'Hello World!'
#    print('sending {!r}'.format(message))
#    s.sendall(message)
#finally:
#    print('closing socket')
#    s.close()
