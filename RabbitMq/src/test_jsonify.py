from capture_datad import MyDaemon
import unittest
import flowd

class TestJsonifyNetflow(unittest.TestCase):

    def setUp(self):
        self.daemon = MyDaemon("/tmp/testing")
        
        #  create the netflow inputs
        netflow_fd = open("raw_netflow.binary")
        self.netflow_samples = []
        for rec in netflow_fd:
            self.netflow_samples.append(rec.strip())
        netflow_fd.close()

    def test_simple(self):
        parsed = flowd.Flow(blob = self.netflow_samples[5])
        sample_rec = self.daemon.jsonify_netflow(parsed)
        assertTrue('{"src_addr": "127.0.0.1", "port": 41959, "proto": 6}', sample_rec)
