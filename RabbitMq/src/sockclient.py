#!/usr/bin/env python


import socket
import flowd
import os
import sys
import getopt
import json
import pika

def usage():
	print >> sys.stderr, "sockclient.pl (flowd.py version %s)" % \
	    flowd.__version__
	print >> sys.stderr, "Usage: reader.pl [options] [flowd-socket]";
	print >> sys.stderr, "Options:";
	print >> sys.stderr, "      -h       Display this help";
	print >> sys.stderr, "      -v       Print all flow information";
	print >> sys.stderr, "      -u       Print dates in UTC timezone";
	sys.exit(1);

def main():
	verbose = 0
	utc = 0

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'huv')
	except getopt.GetoptError:
		print >> sys.stderr, "Invalid commandline arguments"
		usage()

	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit(0)
		if o in ('-v', '--verbose'):
			verbose = 1
			continue
		if o in ('-u', '--utc'):
			utc = 1
			continue

	if len(args) == 0:
		print >> sys.stderr, "No log socket specified"
		usage()
	if len(args) > 1:
		print >> sys.stderr, "Too many log sockets specified"
		usage()

	if verbose:
		mask = flowd.DISPLAY_ALL
	else:
		mask = flowd.DISPLAY_BRIEF

	s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	s.bind(args[0])
	try:

		while 1:
			flowrec = s.recv(1024)
			flow = flowd.Flow(blob = flowrec)

			jsondata = json.dumps({'src_addr': flow.src_addr, 
									'proto':flow.protocol,
									'port':flow.dst_port})
			
			connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
			channel = connection.channel()
			channel.queue_declare(queue='netflow')
			channel.basic_publish(exchange='',
			                      routing_key='netflow',
			                      body=jsondata)
			
			print " [x] Data Sent"
			connection.close()

		
	except:
		os.unlink(args[0])
		raise

if __name__ == '__main__': main()
