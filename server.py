
#!/usr/bin/env python

#title           :server.py
#description     :This will create a header for a python script.
#author          :Group 8
#date            :13.12.2017
#version         :0.1
#usage           :python server.py
#notes           :
#python_version  :2.7.12 
#==============================================================================

# Import modules
import sys
import os
import errno

import socket
import struct
import threading
import time 
from time import sleep

# Constants
CHUNK_SIZE = 4096
FILE_NAME = 'received_file'
ADDR_1 = '10.0.0.3'
ADDR_2 = '10.1.0.3'
PORT = 8080 

CONNECTION_LIST = [] 

###
# Functions
###

# Create server socket and start listening    	 
def start_server((host, port), socketNr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Created TCP server socket " + str(socketNr) + ".")
    try:
    	sock.bind((host, port))
    	print('Binding to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	sys.exit()
    sock.listen(1)
    print("Server socket " + str(socketNr) + " now listening.")
    return sock

# calculate the number of chunks to be received
def get_noOfChunks(bytes, chunkSize):
    noOfChunks = bytes/chunkSize
    if (bytes%chunkSize):
    	noOfChunks += 1
    print("Number of chunks to be received: " + str(noOfChunks))
    return noOfChunks

def monitor_connection_state(address, socket):

    print address, " start monitoring connection state"
    CONNECTION_LIST.append(socket)
    hbthread = threading.Thread(target = heartbeat, args=(address,socket, ))
    hbthread.start();

def heartbeat(address, socket):

    global CONNECTION_LIST

    connectionValid = True

    while connectionValid:
	response = os.system("ping -c 1 " + arg)
		
	if response == 0:
             print address, " is still connected!"
			
	else:
	    connectionValid = False	
	    CONNECTION_LIST.remove(socket)		
			
	    #TODO register last received packet
			
	    print address, " is disconnected, remove connection!"
      	sleep(1)

def start_heartbeat(arg):
    while True:
	response = os.system("ping -c 1 " + arg)
	if response == 0:
            print arg, " is up!"
	    openSocket(arg, arg=='10.0.0.3')
			
	else:
	    print arg, " is down!"
	    closeSocket(arg, arg=='10.0.0.3')
	sleep(1)

# Helper funciton to recv n bytes or return None if EOF is hit
def recvall(sock, count):
    buf = b''
    while count:
    	newbuf = sock.recv(count)
 	if not newbuf: return None
	buf += newbuf
	count -= len(newbuf)
    return buf


# Receive data 	
def recv_data(sock):
    global dataList
    global noOfChunks
    global sizeOfDataRecv
    global fileTransferComplete
    
    global total_recv
    global bytes_recv
    global sizeInBytes

    global start
    global end
	
    # Start timer
    start = time.time()

    # Check if first chunk with data length has already been received
    if sizeOfDataRecv == False:
	try:		
	    bytesBuf = recvall(sock, 4)
	    size_bytes, = struct.unpack('!I', bytesBuf)
 	    bytes = recvall(sock, size_bytes)
	except socket.error, e:
	    errorcode = e[0]
	    if errorcode == errno.ECONNRESET:
	        print("Couln't receive size of data. Error Code : " + str(errorcode) + ' Message ' + e[1])
	    return False
  	sizeOfDataRecv = True
        sizeInBytes = bytes
	print("Received size of data in bytes: " + bytes)
  	noOfChunks = get_noOfChunks(int(bytes), CHUNK_SIZE) 
	
    else: # sizeOfData has already been received -> receive chunks
	while total_recv < noOfChunks:
	    # Receive number of Chunk
	    try:
		# noOfChunk is packed into 4 bytes
	    	noOfChunkBuf = recvall(sock, 4)
	    	noOfChunk, = struct.unpack('!I', noOfChunkBuf)
	    except socket.error, e:
		errorcode = e[0]
		#if errorcode == errno.ECONNRESET:
		print("Couln't receive number of chunk. Closing connection. Error Code : " + str(errorcode) + ' Message ' + e[1])
		sock.shutdown(0)
		sock.close()
		#return False
		
		    
	      	
	    # Receive size of chunk
	    try:
		# sizeBuf is packed into 4 bytes
	    	sizeBuf = recvall(sock, 4)
	    	size, = struct.unpack('!I', sizeBuf)
	    except socket.error, e:
		errorcode = e[0]
		#if errorcode == errno.ECONNRESET:
		print("Couln't receive length of data. Closing connection. Error Code : " + str(errorcode) + ' Message ' + e[1])
		sock.shutdown(0)
		sock.close()
		#return False

	    # Receive actual data
	    try:
	    	chunk = recvall(sock, size) 
	    except socket.error, e:
		errorcode = e[0]
		#if errorcode == errno.ECONNRESET:
		print("Couln't receive chunk data. Closing connection. Error Code : " + str(errorcode) + ' Message ' + e[1])
		sock.shutdown(0)
		sock.close()
		#return False
	

	    # noOfChunk is packed into 4 bytes
	    #noOfChunkBuf = recvall(sock, 4)
	    #noOfChunk, = struct.unpack('!I', noOfChunkBuf)
	    # data length is packed into 4 bytes
	    #sizeBuf = recvall(sock, 4)
	    #size, = struct.unpack('!I', sizeBuf)
	    # Recv actual data
	    #chunk = recvall(sock, size) 
	    dataList.insert(noOfChunk, chunk)
    	    total_recv += 1
   	    bytes_recv += len(chunk)
	    print("Received chunk nr " + str(noOfChunk) + ", size in bytes: " + str(len(chunk)))
	    print("Chunks received: " + str(total_recv) + "/" + str(noOfChunks) + ", bytes received: " + str(bytes_recv) + "/" + str(sizeInBytes))
	
	fileTransferComplete = True
	end = time.time()
	transfer_time = end - start
	print("time: " + str(transfer_time))
	

# Store data in file
def store_data(fileName):
    global dataList
	
    total_len=sum([len(i) for i in dataList])
    print("Data transfer complete! Received " + str(total_len) + " bytes.")

    # Deletes file so that we don't append to existing files
    if os.path.isfile(fileName):
	#fileName += '_new'
	os.remove(fileName)
    for data in dataList:
	f1 = open(fileName, 'ab')
	f1.write(data)
	f1.close()
    size = os.stat(fileName).st_size
    print("Wrote data to file '" + fileName + "', length of file: " + str(size))

def listen_For_Connections(socket):
    global fileTransferComplete
    
    #connection, client_addr = socket.accept()
    #print("Got first connection from: " + str(client_addr))

    connection = 0
    while fileTransferComplete == False:
	if connection == None:
	    connection, client_addr = socket.accept()
    	    print("Got first connection from: " + str(client_addr))
	    recv_data(conneciton)
	else:
	    recv_data(connection)
    	
   
    store_data(FILE_NAME) 
    connection.shutdown(0)
    connection.close()
    socket.shutdown(0)
    socket.close()
           
	
###
# Main
###

dataList = []
noOfChunks = None
total_recv = 0
bytes_recv = 0
sizeInBytes = 0

sizeOfDataRecv = False
fileTransferComplete = False
socket1 = None
socket2 = None

start = 0
end = 0

# Start server sockets
socket1 = start_server(('10.0.0.3', PORT), 1)
socket2 = start_server(('10.1.0.3', PORT), 2)

socket1Thread = threading.Thread(target = listen_For_Connections, args=(socket1, ))
socket1Thread.start()

#socket2Thread = threading.Thread(target = listen_For_Connections, args=(socket2, ))
#socket2Thread.start()




# TODO add second socket









