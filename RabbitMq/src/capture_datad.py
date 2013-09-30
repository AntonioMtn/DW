#!/usr/bin/env python

import socket
import flowd
import os
import sys
import getopt
import json
import pika
import sys, time
import BaseHTTPServer
import logging

from daemon import Daemon

class MyDaemon(Daemon):
    def run(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.bind("/tmp/flowd.sock")

        HOST_NAME = '127.0.0.1'
        PORT_NUMBER = 8000

        try:
            httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
            log.info(time.asctime() + "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
                httpd.server_close()
                log.info(time.asctime() + "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))

            while 1:
                flowrec = s.recv(1024)
                flow = flowd.Flow(blob = flowrec)
                jsondata = self.jsonify_netflow(flow)
            
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                channel = connection.channel()
                channel.queue_declare(queue='netflow')
                channel.basic_publish(exchange='',
                                      routing_key='netflow',
                                      body=jsondata)
                
                logging.info(" [x] Data Sent")
                connection.close()

        except Exception, e:
            logging.info(e)
            os.unlink(args[0])
            raise

    def jsonify_netflow(self, netflow_rec):
        jsondata = json.dumps({'src_addr': netflow_rec.src_addr, 
            'proto':netflow_rec.protocol,
            'port':netflow_rec.dst_port})
        return jsondata

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
     def do_HEAD(s):
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()
     def do_GET(s):
         """Respond to a GET request."""
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()
         s.wfile.write("<html><head><title>Here is a pong</title></head>")
         s.wfile.write("<body><p>PONG.. Service is running</p>")
         s.wfile.write("</body></html>")

if __name__ == "__main__":
    logging.basicConfig(filename='example.log',level=logging.INFO)
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
