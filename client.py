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
CHUNK_SIZE = 4096
PORT = 8080

sizeOfDataSent = False
socket1 = None
socket2 = None
data = None
state = {'sta1-wlan0':{'socket':None, 'ap':None}, 'sta1-wlan1':{'socket':None, 'ap':None}}


###
# Functions
###

# valon scanning thing
def monitorInterfacesStatus():
	global lastInterfaces
	global socket1
	global socket2
       	global data
	global state
	global socket1Thread
       	
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
		    if interfaces['sta1-wlan0'] == 'off/any':
		        print 'stop socket1' #close the socket
			socketThreadStatus[1] = False		
			socket1.shutdown(0)
			socket1.close()
		    elif lastInterfaces['sta1-wlan0'] == 'off/any':
		        print 'socket1 '+ interfaces['sta1-wlan0'] #just open the socket with the new ap
			socketThreadStatus[1] = True			
			
			socket1 = initSocket()
			if connect(socket1,interfaceToIP[interfaces['sta1-wlan0']] , PORT) == True:
			    socket1Thread = threading.Thread(target=send_data, args=(socket1,1, ))
			    socket1Thread.start()			
		    else:
			print("close socket and reopen with new ap")
			print("Socket1 connected with " + interfaces['sta1-wlan0'])
			socketThreadStatus[1] = False		
			socket1.shutdown(0)
			socket1.close()
			
			socket1 = initSocket()
			socketThreadStatus[1] = True
			if connect(socket1,interfaceToIP[interfaces['sta1-wlan0']] , PORT) == True:
			    socket1Thread = threading.Thread(target=send_data, args=(socket1,1, ))
			    socket1Thread.start()
		        print 'socket1 '+interfaces['sta1-wlan0'] #close and open the socket with the new ap

		    lastInterfaces['sta1-wlan0'] = interfaces['sta1-wlan0']
			
		
		    
	    time.sleep(1)

   

    
###		
# Helper functions
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
    print("Length of data in bytes: " + str(bytes))
    return bytes

# calculate the number of chunks to be created
def get_noOfChunks(bytes, chunkSize):
    noOfChunks = bytes/chunkSize
    if (bytes%chunkSize):
    	noOfChunks += 1
    print("Number of chunks: " + str(noOfChunks))
    return noOfChunks   

def get_dataList(data, bytes):
    dataList = []
    dataList.append(bytes) # add the size of the data as firste element
    for i in range(0, bytes+1, CHUNK_SIZE): # add the chunks to the list
    	dataList.append(data[i: i+CHUNK_SIZE])
    print("Elements in dataList: " + str(len(dataList)))
    return dataList

###
# Socket functions
###

# Initialize socket      	 
def initSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("TCP client socket created.")
    return sock

# Bind socket to interface / IP address
def bind(sock, host, port):
    try:
    	sock.bind((host, port))
    	print('Binding to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	#sys.exit()

# Connect socket to the port where H1 is listening
def connect(sock, host, port):
    connectionSuccessful = False
    try:
    	sock.connect((host, port))
    	print('Connecting to ' + host + ' on port ' + str(port))
    except socket.error , msg:
        print('Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    	return connectionSuccessful 
    connectionSuccessful = True
    return connectionSuccessful

# Send data from socket1 or socket2
def send_data(sock, socketNr):
    global dataList
    global noOfChunks
    global sizeInBytes

    global socketThreadStatus
    global sendData

    global chunks_sent
    global bytes_sent
    global total_sent1
    global total_sent2
    
    global sizeOfDataSent

    #while len(dataList) > 0:
    while chunks_sent < noOfChunks and socketThreadStatus[socketNr]: # and send data
	#check if first chunk with sizeOfData has already been sent
	if sizeOfDataSent == False:
	    sizeOfData = dataList.pop(0) # remove sizeOfData from list so that chunks start at dataList[0]
	    print("sizeOfData: " + str(sizeOfData))
	    pack = struct.pack('!I', len(str(sizeOfData)))+str(sizeOfData)
	
	    while True:
	    	try:
	     	    sock.sendall(pack)
	    	except socket.error, e:
	   	    errorcode = e[0]
	      	    if errorcode == errno.ECONNRESET:
		        print("Couldn' sent size of data. Error Code: " + str(errorcode) + ', Message: ' + e[1])
		    continue
	        break
	    sizeOfDataSent = True
	    print("Sent data size: " + str(sizeOfData))

	else: # sizeOfData has already been sent -> sent chunks
 	    #if total_sent1 <= total_sent2:
	    if True:
		if socketNr == 1:
		    noOfChunk = total_sent1
		    noOfChunk_fmt = struct.pack('!I', noOfChunk)
	    	    chunk = dataList[total_sent1]
	    	    lenChunk_fmt = struct.pack('!I', len(chunk))
		    pkt = noOfChunk_fmt + lenChunk_fmt + chunk
		else:
		    noOfChunk = total_sent2
		    noOfChunk_fmt = struct.pack('!I', noOfChunk)
	    	    chunk = dataList[total_sent2]
	    	    lenChunk_fmt = struct.pack('!I', len(chunk))
		    pkt = noOfChunk_fmt + lenChunk_fmt + chunk
	    print("length of pkt: " + str(len(pkt)))
	    # Send chunk	
	    while True:
		try:
		    sock.sendall(pkt) # send no of chunk + length of chunk + actual data
		except socket.error, e:
		   if e.errno == errno.ECONNRESET:
			print("Couln't sent chunk")
		   continue
		break

            if socketNr ==1:
		total_sent1 += 1
	  	print("Socket1 sent chunk number " + str(total_sent1) + ", size in bytes: " + str(len(chunk)))
            else:
		total_sent2 -=1 
	        print("Socket2 sent chunk number " + str(total_sent2) + ", size in bytes: " + str(len(chunk)))
	    
	    bytes_sent += len(chunk)
	    chunks_sent += 1
	    print("Chunks sent: " + str(chunks_sent) + "/" + str(noOfChunks) + ", bytes sent: " + str(bytes_sent) + "/" + str(sizeInBytes))

###
# Main
###

# Allocate file variables
inputFile = sys.argv[1]
data = get_fileData(inputFile)
lastInterfaces = {'sta1-wlan0':'off/any', 'sta1-wlan1':'off/any'}
interfaceToIP = {'ap1-ssid':'10.0.0.3', 'ap2-ssid':'10.1.0.3', 'ap3-ssid':'10.1.0.3', 'fast-ssid':'10.1.0.3'}

# Split chunks
sizeInBytes = get_sizeInBytes(data)
dataList = get_dataList(data, sizeInBytes)
noOfChunks = get_noOfChunks(sizeInBytes, CHUNK_SIZE)

chunks_sent = 0 # total number of chunks sent
bytes_sent = 0 # total number of bytes sent
total_sent1 = 0 # number of chunks sent from socket1
total_sent2 = noOfChunks-1 # number of chunks sent from socket2

socketThreadStatus = {1 : False, 2 : False}
sendData = False

# Initialize the sockets
socket1 = initSocket()
socket2 = initSocket()


threadWork = threading.Thread(target=monitorInterfacesStatus)
threadWork.start()

socket1Thread = threading.Thread(target=send_data, args=(socket1,1, ))


