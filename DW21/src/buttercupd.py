#!/usr/bin/env python

import logging
import sys
import os

from Rabbit_Flowd_Connector import Rabbit_Flowd_Connector
from Webserver import Status_Server
from daemonize import Daemonize
from ConfigParser import SafeConfigParser
from subprocess import Popen, PIPE


class Flowd_RabbitD():
    
    pid = "/tmp/flowd_rabbit.pid"

    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fh = logging.FileHandler("/tmp/flowd_rabbitd.log", "w")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]

    def run(self):
      self.logger.info("Start")
      try:

        #Initialize flowd connector
        ret = Rabbit_Flowd_Connector().run(self.logger,self.queue,self.rabbit_server)

        #start flowd connector
        self.startFlowd()

        self.logger.info("Done with connector. Initializing web server")
        
        #Initialize webserver
        Status_Server().run(self.logger, self.host,self.port)
        

      except Exception, e:
        self.logger.info("Error running deamon...%s:" % (e))
        os.unlink(self.pid)


    def main(self,conf_file):
      
        self.readConfig(conf_file)
        daemon = Daemonize(app="FlowdConnector",pid=self.pid,action=self.run, keep_fds=self.keep_fds)
        daemon.start()


    def readConfig(self,conf_file):
        
        parser = SafeConfigParser()
        parser.read(conf_file)

        try:
            host = parser.get('options','host')
            port = parser.get('options','port')
            queue = parser.get('options','queue')
            rabbit_server = parser.get('options','rabbit_server')

        except Exception, e:
            host = "127.0.0.1"
            port = "8000"
            queue = "netflow"
            rabbit_server = "127.0.0.1"

        #Use defaults in case they were not specified in config file
        self.host = host
        self.port = port
        self.queue = queue
        self.rabbit_server = rabbit_server

    
    def startFlowd(self):
        Popen(["flowd"], stdout=PIPE)


    def stop(self,conf_file):
        self.readConfig(conf_file)
        Rabbit_Flowd_Connector().stop(self.logger)
        Status_Server().stop(self.logger, self.host,self.port)

        try:
            os.unlink(self.pid)
        except Exception,e:
            pass


    

if __name__ == "__main__":

    connector = Flowd_RabbitD()

    if len(sys.argv) == 4:
        if 'start' == sys.argv[3] and '-c' == sys.argv[1]:
            connector.main(sys.argv[2])
        elif 'stop' == sys.argv[3] and '-c' == sys.argv[1]:
            connector.stop(sys.argv[2])
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s -c start|stop" % sys.argv[0]
        sys.exit(2)


    
