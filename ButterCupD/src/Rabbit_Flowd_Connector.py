#!/usr/bin/env python

import socket
import flowd
import json
import pika
import os
import signal

from threading import Thread
from subprocess import Popen, PIPE

class Rabbit_Flowd_Connector():
    
    def run(self, logging,queue, rabbit_server):

        try:
            
            logging.info("Running flowd to rabbit connector")
            t = Thread(target=self.collect_data, args=(logging,rabbit_server,queue,))
            t.start()

            
            #self.collect_data(logging,rabbit_server,queue,)

        except Exception, e:
            raise

    def collect_data(self, logging,rabbit_server,queue):
        
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            s.bind("/tmp/flowd.sock")

            logging.info("Starting flowd_rabbit connector: %s - %s" % (rabbit_server,queue))

            while 1:
                    flowrec = s.recv(1024)
                    flow = flowd.Flow(blob = flowrec)
                    
                    jsondata = self.jsonify_netflow(flow)

                    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_server))
                    channel = connection.channel()
                    channel.queue_declare(queue=queue)
                    channel.basic_publish(exchange='',
                                          routing_key='netflow',
                                          body=jsondata)
                    
                    connection.close()
        except Exception, e:
            logging.info(e)
            os.unlink("/tmp/flowd.sock")
            raise

    def stop(self, logging):
        
        p  = Popen(["lsof", "-w"], stdout=PIPE)
        p1 = Popen(["grep", "/usr/local/sbin/flowd"], stdin=p.stdout, stdout=PIPE)

        out = p1.communicate()[0]

        logging.info("process: " + out)
                      
        if out is not None and out != "":
           out = out.split()[1]
           logging.info("process: " + out)
           os.kill(int(out),signal.SIGKILL)
        
        try:
            os.unlink("/tmp/flowd.sock")
        except Exception:
            #if we are here is because flowd.sock does not exist
            pass



    def jsonify_netflow(self, netflow_rec):

        jsondata = json.dumps({'data':self.checkattr(netflow_rec,"data"),
                                'src_addr':self.checkattr(netflow_rec,"src_addr"),
                                'dst_addr':self.checkattr(netflow_rec,"dst_addr"),
                                'agent_addr':self.checkattr(netflow_rec,"agent_addr"),
                                'gateway_addr':self.checkattr(netflow_rec,"gateway_addr"),
                                'octets':self.checkattr(netflow_rec,"octets"),
                                'packets':self.checkattr(netflow_rec,"packets"),
                                'src_addr_af':self.checkattr(netflow_rec,"src_addr_af"),
                                'dst_addr_af':self.checkattr(netflow_rec,"dst_addr_af"),
                                'agent_addr_af':self.checkattr(netflow_rec,"agent_addr_af"),
                                'gateway_addr_af':self.checkattr(netflow_rec,"gateway_addr_af"),
                                'flow_ver':self.checkattr(netflow_rec,"flow_ver"),
                                'fields':self.checkattr(netflow_rec,"fields"),
                                'tag':self.checkattr(netflow_rec,"tag"),
                                'recv_sec':self.checkattr(netflow_rec,"recv_sec"),
                                'recv_usec':self.checkattr(netflow_rec,"recv_usec"),
                                'tcp_flags':self.checkattr(netflow_rec,"tcp_flags"),
                                'protocol':self.checkattr(netflow_rec,"protocol"),
                                'tos':self.checkattr(netflow_rec,"tos"),
                                'src_port':self.checkattr(netflow_rec,"src_port"),
                                'dst_port':self.checkattr(netflow_rec,"dst_port"),
                                'if_ndx_in':self.checkattr(netflow_rec,"if_ndx_in"),
                                'if_ndx_out':self.checkattr(netflow_rec,"if_ndx_out"),
                                'sys_uptime_ms':self.checkattr(netflow_rec,"sys_uptime_ms"),
                                'agent_sec':self.checkattr(netflow_rec,"agent_sec"),
                                'agent_usec':self.checkattr(netflow_rec,"agent_usec"),
                                'netflow_ver':self.checkattr(netflow_rec,"netflow_ver"),
                                'flow_start':self.checkattr(netflow_rec,"flow_start"),
                                'flow_finish':self.checkattr(netflow_rec,"flow_finish"),
                                'src_as':self.checkattr(netflow_rec,"src_as"),
                                'dst_as':self.checkattr(netflow_rec,"dst_as"),
                                'src_mask':self.checkattr(netflow_rec,"src_mask"),
                                'dst_mask':self.checkattr(netflow_rec,"dst_mask"),
                                'engine_type':self.checkattr(netflow_rec,"engine_type"),
                                'engine_id':self.checkattr(netflow_rec,"engine_id"),
                                'flow_sequence':self.checkattr(netflow_rec,"flow_sequence")})


        return jsondata


    def checkattr(self,row, name):
        if hasattr(row, name):
            return getattr(row,name)
        
        return ""