import unittest
import flowd
import os
from capture_datad import MyDaemon

class TestJsonifyNetflow(unittest.TestCase):

    def setUp(self):
        self.daemon = MyDaemon("/tmp/testing")
        
        #  create the netflow inputs
        test_dir = os.path.dirname(__file__)
        raw_netflow_filename = os.path.join(test_dir, 'raw_netflow.binary')
        netflow_fd = open(raw_netflow_filename)
        self.netflow_samples = []
        for rec in netflow_fd:
            self.netflow_samples.append(rec.strip())
        netflow_fd.close()

    def test_simple(self):
        parsed = flowd.Flow(blob = self.netflow_samples[5])
        sample_rec = self.daemon.jsonify_netflow(parsed)
        self.assertEqual('{"src_addr": "127.0.0.1", "port": 41959, "proto": 6}', sample_rec)
