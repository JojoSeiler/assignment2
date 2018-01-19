
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
import sys
import errno
import socket
import struct
#import os
#import hashlib

# Constants
#('localhost', 80)
ADDR = ('localhost', 80)
#WLAN0_ADDR = ('10.0.0.2', 80)
#WLAN1_ADDR = ('10.1.0.2', 80)
#H1_ADDR = ('10.0.0.3', 80)
CHUNK_SIZE = 4096


###
# Functions
###

# read the contents of a file
def get_fileData(inputFile):
    f = open(inputFile, 'rb')
    data = f.read() # read the entire content of the file
    f.close()
    return data

# get the length of data, ie size of the input file in bytes
def get_sizeInBytes(data):
    bytes = len(data)
    #print("Length of data in bytes: " + str(bytes))
    return bytes

# calculate the number of chunks to be created
def get_noOfChunks(bytes, chunkSize):
    noOfChunks = bytes/chunkSize
    if (bytes%chunkSize):
    	noOfChunks += 1
    print("Number of chunks: " + str(noOfChunks))
    return noOfChunks

# store chunks in array
def get_dataList(data, bytes):
    dataList = []
    for i in range(0, bytes+1, CHUNK_SIZE):
    	dataList.append(data[i: i+CHUNK_SIZE])
    return dataList

# Initialize socket      	 
def initSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP client socket created.")
    return sock

# Bind socket to interface / IP address
def bind(sock, host, port):
    try:
    	sock.bind((host, port))
    	print('Binding to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	sys.exit()

# Connect socket to the port where H1 is listening
def connect(sock, host, port):
    try:
    	sock.connect((host, port))
    	print('Connecting to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	sys.exit()

# Send size of data in bytes
def send_sizeOfData(sock, data):
    bytes = get_sizeInBytes(data)
    pack = struct.pack('!I', len(str(bytes)))+str(bytes)
    
    # TODO choose strongest available connection: e.g. sock = new sock ...
    while True:
    	try:
	    sock.sendall(pack)
    	except socket.error, e:
	    errorcode = e[0]
	    if errorcode == errno.ECONNRESET:
	    	# TODO handle disconnection: e.g. close & reopen socket
		# TODO handle other errors/exceptions, socke.timeout
		print("Couln't sent size of data. Error Code : " + str(errorcode) + ' Message ' + e[1])
		continue
	break
    print("Sent data size: " + str(bytes))
     

# Send file data
def send_data(sock, data):  
    total_sent = 0
    bytes_sent = 0
    bytes = get_sizeInBytes(data)
    noOfChunks = get_noOfChunks(bytes, CHUNK_SIZE)
    dataList = get_dataList(data, bytes)
    print("length of datalist: " + str(len(dataList)))

    # TODO choose strongest available connection: e.g. sock = new sock ...
    while total_sent < noOfChunks:
	chunk = dataList[total_sent]
	pkt = struct.pack('!I', len(chunk))+chunk

	while True:
	    try:
		sock.sendall(pkt) # send chunk data + length (network = big-endian unsigned int)
	    except socket.error, e:
		if e.errno == errno.ECONNRESET:
		     # TODO handle disconnection: e.g. close & reopen socket
		     # TODO handle other errors/exceptions
		     print("Couln't sent chunk number " + str(total_sent))
		     continue
	    break  
        total_sent += 1
	bytes_sent += len(chunk)
 	print("Sent chunk " + str(total_sent) + "/" + str(noOfChunks) + ", size in bytes: " + str(len(chunk)))
    
    print("File Transfer Complete! Sent " + str(bytes_sent) + "/" + str(bytes) + " bytes.")
    sock.shutdown(1) # done sending
 
###
# Main
###

# Allocate file variables
inputFile = sys.argv[1]
data = get_fileData(inputFile)

# Create TCP client socket
sock = initSocket()
# TODO get first server_address correctly
server_addr = 'localhost'
server_port = 8080
connect(sock, server_addr, server_port)

# Start sending data
send_sizeOfData(sock,data) 
send_data(sock, data)
sock.close



