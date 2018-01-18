
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
import socket
import struct
import threading
import time

# Constants

#('localhost', 80)
ADDR = ('localhost', 80)
CHUNK_SIZE = 4096
FILE_NAME = 'received_file'
 
###
# Functions
###

# Start server      	 
def start_server((host, port)):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP server socket created.")
    try:
    	sock.bind((host, port))
    	print('Binding to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	sys.exit()
    sock.listen(1)
    print('Server socket now listening.')
    return sock

# calculate the number of chunks to be created
def get_noOfChunks(bytes, chunkSize):
    noOfChunks = bytes/chunkSize
    if (bytes%chunkSize):
    	noOfChunks += 1
    print("Number of chunks: " + str(noOfChunks))
    return noOfChunks

# helper funciton to recv n bytes or return None if EOF is hit
def recvall(sock, count):
    buf = b''
    while count:
    	newbuf = sock.recv(count)
 	if not newbuf: return None
	buf += newbuf
	count -= len(newbuf)
    return buf

# Receive the size of the data to be received
def recv_sizeOfData(connection):
    while True:
    	try:
	    # length of data size is packed into 4 bytes
	    bytesBuf = recvall(connection, 4)
	    size_bytes, = struct.unpack('!I', bytesBuf)
	    bytes = recvall(connection, size_bytes)	# TODO handle return value None?
    	except socket.error, e:
	    errorcode = e[0]
	    if errorcode == errno.ECONNRESET:
	    	# TODO handle disconnection: e.g. accept new socket
		# TODO handle other errors/exceptions, socket.timeout
		print("Couln't receive size of data. Error Code : " + str(errorcode) + ' Message ' + e[1])
		continue
	break
    print("Length of incoming file in bytes: " + bytes)
    return bytes
		
# Receive data
def recv_Data(connection, bytes):
    total_recv = 0
    noOfChunk = 0
    total_data = []
    noOfChunks = get_noOfChunks(int(bytes), CHUNK_SIZE)
    
    # Receive chunks
    while total_recv < noOfChunks: 
	# noOfChunk is packed into 4 bytes	
	noOfChunkBuf = recvall(connection, 4)
	noOfChunk, = struct.unpack('!I', noOfChunkBuf)
	# data length is packed into 4 bytes
	sizeBuf = recvall(connection, 4)
	size, = struct.unpack('!I', sizeBuf)
	# Recv actual data
	data = recvall(connection, size)
	if data == 0:
	    raise RuntimeError("socket connection broken") # TODO
	total_data.append(data)
	total_recv += 1
        print("chunk nr: " + str(noOfChunk))
	print("Received chunk nr " + str(total_recv) + "/" + str(noOfChunks) + ", size in bytes: " + str(len(data)))
	
    total_len=sum([len(i) for i in total_data ])
    connection.shutdown(0) # done receiving
    connection.close()
    print("Data transfer complete! Received " + str(total_len) + "/" + bytes + " bytes.")
    return total_data

# Store data in file
def store_Data(fileName, dataList):
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
    global dataList
    global count
    
    while True:
        # wait to accept a connection
        connection, client_addr = sock.accept()
        print('Got connection from: ', client_addr)
    
        count = recv_sizeOfData(connection)
        dataList = recv_Data(connection, count)
        #store_Data(FILE_NAME, dataList)	

###
# Main
###

server_addr = 'localhost'
server_port = 8080
dataList = None
count = 0

slowSock = start_server(('10.0.0.3', server_port))
fastSock = start_server(('10.1.0.3', server_port))
slowSockThread = Thread(target = listen_For_Connections, args=(slowSocket, ))
slowSockThread.start()
fastSockThread = Thread(target = listen_For_Connections, args=(fastSocket, ))
fastSockThread.start()






