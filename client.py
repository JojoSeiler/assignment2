
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
import subprocess
import time
import argparse
import threading


# Constants
#('localhost', 80)
ADDR = ('localhost', 80)
#WLAN0_ADDR = ('10.0.0.2', 80)
#WLAN1_ADDR = ('10.1.0.2', 80)
#H1_ADDR = ('10.0.0.3', 80)
CHUNK_SIZE = 4096
PORT = 8080
sizeOfDataSent = False
slowSocket = None
fastSocket = None
data = None


###
# Functions
###

# valon scanning thing
def monitorInterfacesStatus():
	global lastInterfaces
	global slowSocket
	global fastSocket
       	global data	

	parser = argparse.ArgumentParser(description='Display WLAN signal strength.')
	parser.add_argument(dest='interface', nargs='?', default='sta1-wlan1',
		            help='wlan interface (default: wlan0)')
	args = parser.parse_args()

	print '\n---Press CTRL+Z or CTRL+C to stop.---\n'
		
	interfaces = {'sta1-wlan0':'off/any', 'sta1-wlan1':'off/any'}
	while True:
	    cmd = subprocess.Popen('iwconfig', shell=True,
		                   stdout=subprocess.PIPE)
	    for line in cmd.stdout:
		if 'ESSID' in line:
		    interface = line.split(' ')[0]
		    if 'off/any' in line:
			value = 'off/any'
		    else:
		        value = line.split('"')[1]

		    interfaces[interface] = value
		
		if lastInterfaces['sta1-wlan0'] != interfaces['sta1-wlan0']:
		    print interfaces['sta1-wlan0']
		    if interfaces['sta1-wlan0'] != 'off/any':
			print 'open slowSocket'
			if (slowSocket==None):
   			    addr = '10.0.0.3'
			    slowSocket=initSocket()
			# bind socket
		        connect(slowSocket, addr, PORT) # TODO handle connection fail
			if sizeOfDataSent == False:			    
				sendSizeThread = threading.Thread(target = send_sizeOfData, args=(slowSocket, data, ))
				sendSizeThread.start()
				sendSizeThread.join()
			sendDataSlowSocketThread = threading.Thread(target = send_data, args=(slowSocket, data, ))
			sendDataSlowSocketThread.start()
		    lastInterfaces['sta1-wlan0'] = interfaces['sta1-wlan0']

		if lastInterfaces['sta1-wlan1'] != interfaces['sta1-wlan1']:
		    if interfaces['sta1-wlan1'] != 'off/any':
			print 'open fastSocket'
			if (fastSocket==None):
   			    addr = '10.1.0.3'
			    fastSocket=initSocket()
			# bind socket
			connect(fastSocket, addr, PORT) # TODO handle connection fail
			if sizeOfDataSent == False:			    
				sendSizeThread = threading.Thread(target = send_sizeOfData, args=(fastSocket, data, ))
				sendSizeThread.start()
				sendSizeThread.join()
			sendDataFastSocketThread = threading.Thread(target = send_data, args=(fastSocket, data, ))
			sendDataFastSocketThread.start()
		    lastInterfaces['sta1-wlan1'] = interfaces['sta1-wlan1']
		
		print lastInterfaces
		     
	    time.sleep(1)


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
    global sizeOfDataSent
    bytes = get_sizeInBytes(data)
    pack = struct.pack('!I', len(str(bytes)))+str(bytes)
    
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
    sizeOfDataSent = True
    print("Sent data size: " + str(bytes))
     

# Send file data
def send_data(sock, data):
    global dataList  
    global bytes
    global noOfChunks

    noOfChunk = 1
    total_sent = 0
    bytes_sent = 0
    
    print("length of datalist: " + str(len(dataList)))

    # TODO choose strongest available connection: e.g. sock = new sock ...

    while len(dataList) > 0:
 

	chunk = dataList[total_sent]
        noOfChunk_fmt = struct.pack('!I', noOfChunk)
   	lenChunk_fmt = struct.pack('!I', len(chunk))
	pkt = noOfChunk_fmt + lenChunk_fmt +chunk

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
	noOfChunk += 1
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
lastInterfaces = {'sta1-wlan0':'off/any', 'sta1-wlan1':'off/any'}
interfaceToIP = {'ap1-ssid':'10.0.0.3', 'ap2-ssid':'10.1.0.3', 'ap3-ssid':'10.1.0.3', 'fast-ssid':'10.1.0.3'}



# Split chunks
bytes = get_sizeInBytes(data)
dataList = get_dataList(data, bytes)
noOfChunks = get_noOfChunks(bytes, CHUNK_SIZE)
threadWork = threading.Thread(target=monitorInterfacesStatus)
threadWork.start()


