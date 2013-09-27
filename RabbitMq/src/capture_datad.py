#!/usr/bin/env python

import socket
import flowd
import os
import sys
import getopt
import json
import pika
import sys, time
from daemon import Daemon

class MyDaemon(Daemon):
	def run(self):
		s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		s.bind("/tmp/flowd.sock")
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

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/packet_capture.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
