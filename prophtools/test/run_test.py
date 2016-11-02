# -*- coding: utf-8 -*-

import unittest
import os
import prophtools.operations.run as run
import tempfile
import shutil
import prophtools.utils.loggingtools as loggingtools
import sys
import StringIO
import mock
from prophtools.common.method import ProphNet
from prophtools.common.graphdata import GraphDataSet


class TestLocalRunExperimentFunctions(unittest.TestCase):
    """
    Test for RunExperiment class
    """

    def setUp(self):
        config_test_data = """
[run]
data_path = .
corr_function = pearson
matfile =
"""
        self.tempdir = tempfile.mkdtemp()
        self.configname = 'config.cfg'
        fo = open(os.path.join(self.tempdir, self.configname), 'w')
        fo.write(config_test_data)
        fo.close()

        fo = open(os.path.join(self.tempdir, 'mockmat.mat'), 'w')
        fo.close()

        tmp_log = os.path.join(self.tempdir, 'run.log')
        self.log = loggingtools.init_generic_log(tmp_log, 2)

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.tempdir)

    def test_required_parameters_missing_returns_without_running(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = run.LocalRunExperiment(cfg_path, 'run', self.log, section_name='run')

        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run([], self.configname)
        os.remove('run.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)

    @mock.patch.object(GraphDataSet, 'read')
    @mock.patch.object(ProphNet, 'propagate')
    def test_required_parameters_required(self, mock_propagate, mock_read):
        cfg_path = os.path.join(self.tempdir, self.configname)
        
        exp = run.LocalRunExperiment(cfg_path, 'run', self.log, section_name='run')
        matfile = os.path.join(self.tempdir, 'mockmat.mat')

        parameters = ['--query', '1', '--src', '0', '--dst', '1', '--matfile', matfile]
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('run.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        mock_read.assert_called_with('.', matfile)
        mock_propagate.assert_called()
        
        self.assertEqual(result, 0)

    def test_required_parameters_non_existing_file_returns_without_running(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = run.LocalRunExperiment(cfg_path, 'run', self.log, section_name='run')

        parameters = ['--query', '1', '--src', '0', '--dst', '1', '--matfile', 'test.mat']
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('run.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestLocalRunExperimentFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
