
#!/usr/bin/env python

#title           :server.py
#description     :This will create a header for a python script.
#author          :Group 8
#date            :15.01.2018
#version         :0.2
#usage           :python server.py
#notes           :
#python_version  :2.7.12 
#==============================================================================

# Import modules
import socket
import sys

# Constants
HOST = '10.0.0.3'
PORT = 5000
ADDR = (HOST,PORT)
BUFFER_SIZE = 4096
 
# Create TCP/IP server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('socket created')
 
# Bind the socket to the port
try:
    server.bind(ADDR)
except socket.error , msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print('starting up on {} port {}'.format(*ADDR))
 
# Listen for incoming connections
server.listen(1)
print('Socket now listening')
 
while True:
    #wait to accept a connection - blocking call
    connection, client_addr = server.accept()
    print('connection from', client_addr)
     
    # Receive the data
    newfile = open('testfile.jpeg', 'w')

    while True:
        data = connection.recv(BUFFER_SIZE)
	if not data: break
	newfile.write(data)
	print('writing file ...')
	
    newfile.close()
    print('finishing wiriting file')
 
    connection.close()
    print('client disconnected')




