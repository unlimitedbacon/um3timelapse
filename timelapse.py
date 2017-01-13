#!/bin/python3
import os
import argparse
from requests import exceptions
from tempfile import mkdtemp
from time import sleep
from urllib.request import urlopen
from um3api import Ultimaker3

cliParser = argparse.ArgumentParser(description=
			'Creates a time lapse video from the onboard camera on your Ultimaker 3.')
cliParser.add_argument('HOST', type=str,
			help='IP address of the Ultimaker 3')
cliParser.add_argument('DELAY', type=float,
			help='Time between snapshots in seconds')
cliParser.add_argument('OUTFILE', type=str,
			help='Name of the video file to create. Recommended formats are .mkv or .mp4.')
options = cliParser.parse_args()

imgurl = "http://" + options.HOST + ":8080/?action=snapshot"

api = Ultimaker3(options.HOST, "Timelapse")
#api.loadAuth("auth.data")

def printing():
	status = None
	# If the printer gets disconnected, retry indefinitely
	while status == None:
		try:
			status = api.get("api/v1/printer/status").json()
			if status == 'printing':
				state = api.get("api/v1/print_job/state").json()
				if state == 'wait_cleanup':
					return False
				else:
					return True
			else:
				return False
		except exceptions.ConnectionError as err:
			status = None
			print_error(err)

def progress():
	p = None
	# If the printer gets disconnected, retry indefinitely
	while p == None:
		try:
			p = api.get("api/v1/print_job/progress").json() * 100
			return "%05.2f %%" % (p)
		except exceptions.ConnectionError as err:
			print_error(err)

def print_error(err):
	print("Connection error: {0}".format(err))
	print("Retrying")
	print()
	sleep(1)

tmpdir = mkdtemp()
filenameformat = os.path.join(tmpdir, "%05d.jpg")
print(":: Saving images to",tmpdir)

if not os.path.exists(tmpdir):
	os.makedirs(tmpdir)

print(":: Waiting for print to start")
while not printing():
	sleep(1)
print(":: Printing")

count = 0

while printing():
	count += 1
	response = urlopen(imgurl)
	filename = filenameformat % count
	f = open(filename,'bw')
	f.write(response.read())
	f.close
	print("Print progress: %s Image: %05i" % (progress(), count), end='\r')
	sleep(options.DELAY)

print()
print(":: Print completed")
print(":: Encoding video")
ffmpegcmd = "ffmpeg -r 30 -i " + filenameformat + " -vcodec libx264 -preset veryslow -crf 18 " + options.OUTFILE
print(ffmpegcmd)
os.system(ffmpegcmd)
