# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
import shutil
import prophtools.utils.loggingtools as loggingtools
import sys
import StringIO
import mock
from prophtools.common.graphdata import GraphDataSet
from prophtools.stats.metrics import PrioritizationTest
from prophtools.common.method import ProphNet

class TestPrioritizationTestFunctions(unittest.TestCase):
    """
    Test for PrioritizationTest class
    """
    def load_test_data(self):
        script_dir = os.path.dirname(__file__)
        absolute_path = os.path.join(script_dir, '../matfiles/')
        self.sample_data = GraphDataSet.read(absolute_path, 'example.mat')
        self.prioritizer = ProphNet(self.sample_data)
        self.prio_test = PrioritizationTest(self.prioritizer)

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        tmp_log = os.path.join(self.tempdir, 'loo.log')
        self.log = loggingtools.init_generic_log(tmp_log, 2)
        self.load_test_data()

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.tempdir)

    def test_compute_rank_normal_case(self):
        scores = [0.3, 0.6, 0.1, 0.0, 0.3]
        expected_rank = 0

        result_rank = self.prio_test.compute_rank(scores, 1)
        self.assertEqual(result_rank, expected_rank)

    def test_compute_rank_edge_case(self):
        scores = [0.3, 0.6, 0.1, 0.0, 0.3]
        expected_rank = 4

        result_rank = self.prio_test.compute_rank(scores, 3)
        self.assertEqual(result_rank, expected_rank)




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPrioritizationTestFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
