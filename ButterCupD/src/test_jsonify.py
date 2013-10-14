import unittest
import flowd
import os
import random
import urllib2
import time
import logging

from threading import Thread
from Webserver import Status_Server
from Rabbit_Flowd_Connector import Rabbit_Flowd_Connector


class UnitTest():

    def __init__(self):
        self.server_running = False
        self.port = random.randint(30000, 40000)
        self.host = '127.0.0.1'
        self.server = Status_Server() #get a reference to the class
        self.server_thread = None
        logging.basicConfig(filename='test.log',level=logging.INFO)

    def initializeWebServer(self):
        
        try:
            
            if(self.server_running == False):
                print "Starting web server"
                self.server_thread = Thread(target=self.server.run,args=(logging,self.host,self.port,))
                self.server_thread.start()
                time.sleep(0.50) #give it some time to start

                self.server_running = True

        except Exception,e:
            logging.info(e)
            return False

    def check_status(self):
        #test to see if the server is up
        print "Server status: " + self.host + " " + str(self.port)
        try:
            code = urllib2.urlopen('http://%s:%s/' % (self.host, str(self.port)), timeout=5).getcode()
            return code
        except urllib2.URLError:
            return None


    def check_health(self):
        print "Testing health check"
        try:
            f = urllib2.urlopen('http://%s:%s/status/healthcheck' % (self.host, str(self.port)), timeout=5)
            data = f.read()
            return data

        except urllib2.URLError:
            return None


    def stop(self):
        self.server.stop(logging,self.host,self.port)


class TestJsonifyNetflow(unittest.TestCase):

    def test_simple(self):
        #  create the netflow inputs
        print "Ceating the netflow inputs"
        test_dir = os.path.dirname(__file__)
        raw_netflow_filename = os.path.join(test_dir, 'raw_netflow.binary')
        netflow_fd = open(raw_netflow_filename)
        self.netflow_samples = []
        for rec in netflow_fd:
            self.netflow_samples.append(rec.strip())
        netflow_fd.close()


        parsed = flowd.Flow(blob = self.netflow_samples[5])
        sample_rec = Rabbit_Flowd_Connector().jsonify_netflow(parsed) #self.daemon.jsonify_netflow(parsed)
        self.assertEqual('{"tcp_flags": 20, "agent_addr_af": 2, "protocol": 6, "engine_type": 0, "gateway_addr": "0.0.0.0", "agent_addr": "127.0.0.1", "src_mask": 0, "agent_usec": 936639000, "if_ndx_out": 0, "octets": 40, "agent_sec": 1380324481, "dst_as": 0, "tag": 0, "sys_uptime_ms": 111976226, "dst_addr_af": 2, "src_port": 7002, "data": {}, "flow_finish": 111848158, "dst_mask": 0, "flow_start": 111848158, "gateway_addr_af": 2, "src_addr": "127.0.0.1", "fields": 1074264750, "src_as": 0, "packets": 1, "src_addr_af": 2, "netflow_ver": 5, "recv_sec": 1380324481, "engine_id": 0, "tos": 0, "if_ndx_in": 0, "flow_sequence": 9363, "recv_usec": 936790, "dst_addr": "127.0.0.1", "flow_ver": 96, "dst_port": 41959}', sample_rec)


    def test_webserver(self):
        ut.initializeWebServer()
        code = ut.check_status()

        self.assertEqual(code,200)

    def test_webserver_health(self):
        ut.initializeWebServer()
        response = ut.check_health()

        flag = True

        if(response is None):
            flag = False


        self.assertEqual(True,flag)

        ut.stop()
        


def main():
    unittest.main()

if __name__ == "__main__":
    global ut

    ut = UnitTest()
    main()