import BaseHTTPServer
import time
import urllib2
import os
import signal
import json

import logging

from subprocess import Popen, PIPE

class HTTPServer(BaseHTTPServer.HTTPServer):

    _continue = True

    def serve_until_shutdown(self):
        while self._continue:
            self.handle_request()

    def shutdown(self):
        self._continue = False
        try:
            # Make a fake request to the server, to really force it to stop.
            # Otherwise it will just stop on the next request.
            code = urllib2.urlopen('http://%s/' % (str(self.server_address))).getcode()
        except urllib2.URLError:
            # If the server is already shut down, we receive a socket error,
            # which we ignore.
            pass

        self.server_close()


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
   
   def do_HEAD(s):
       s.send_response(200)
       s.send_header("Content-type", "text/html")
       s.end_headers()
   def do_GET(s):
       s.send_response(200)
       
       if not "status/healthcheck" in s.path:
         s.send_header("Content-type", "text/plain")
         s.end_headers()
         s.wfile.write("Pong!")
       else:
         s.send_header("Content-type", "application/json")
         s.end_headers()
         s.wfile.write(s.check_process_status())

   def check_process_status(self):
       #check pid exists
       if os.path.exists("/tmp/flowd.sock") and os.path.exists("/tmp/flowd_rabbit.pid"):
          #processes are running. Lets check flowd to make sure its running
          if(self.check_flowd()):
            return json.dumps({'status':'OK'})
          else:
            return json.dumps({'status':'BAD', 'reason' : 'flowd service doesnt look like its running'})
       
       return json.dumps({'status': 'BAD', 'reason' : 'processes are not running'})


   def check_flowd(self):
      p  = Popen(["lsof", "-w"], stdout=PIPE)
      p1 = Popen(["grep", "/usr/local/sbin/flowd"], stdin=p.stdout, stdout=PIPE)

      out = p1.communicate()[0]
              
      if out is not None and out != "":
         return True

      return False
       
       


class Status_Server(object):
   
   def __init__(self):
    self.server = None;

   def run(self, logging,host,port):
    
    try:
        logging.info("Attempting to start the webserver")
        self.HOST_NAME = host
        self.PORT_NUMBER = port

        self.stop(logging,self.HOST_NAME,self.PORT_NUMBER)

        server_address = (self.HOST_NAME, int(self.PORT_NUMBER))
        self.server = HTTPServer((server_address), MyHandler)
        logging.info(time.asctime() + " Server Starts - %s:%s" % (self.HOST_NAME, self.PORT_NUMBER))
        self.server.serve_until_shutdown()

    except Exception, e:
        raise

   def stop(self,logging,host,port):
    if self.server is None:
      #there is probably another instance of the service running, lets kill it first and attempt to startup
      arg = ("%s (LISTEN)" % (port))
      proc  = Popen(["lsof", "-w"], stdout=PIPE)
      proc1 = Popen(["grep", arg], stdin=proc.stdout, stdout=PIPE)
      out = proc1.communicate()[0]
      
      if out is not None and out != "":
          out = out.split()[1]
          logging.info("PID: " + str(out))
          os.kill(int(out),signal.SIGKILL)
          logging.info("Killed process.." + str(out))
      else:
        logging.info("Server is down or never started")
    else:
      self.server.shutdown()

    logging.info(time.asctime() + " Server Stops - %s:%s" % (host, port))
