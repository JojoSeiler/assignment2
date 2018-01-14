# -*- coding: utf-8 -*-
import subprocess
import time
import argparse
import threading








def monitorInterfacesStatus():
	parser = argparse.ArgumentParser(description='Display WLAN signal strength.')
	parser.add_argument(dest='interface', nargs='?', default='sta1-wlan1',
		            help='wlan interface (default: wlan0)')
	args = parser.parse_args()

	print '\n---Press CTRL+Z or CTRL+C to stop.---\n'
	lastInterfaces = {'sta1-wlan0':'off/any', 'sta1-wlan1':'off/any'}	
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
		
		if lastInterfaces != interfaces:
		    lastInterfaces['sta1-wlan0'] = interfaces['sta1-wlan0']
	            lastInterfaces['sta1-wlan1'] = interfaces['sta1-wlan1']
		    print lastInterfaces
		
		     
	    time.sleep(1)





threadWork = threading.Thread(target=monitorInterfacesStatus)
threadWork.start()
