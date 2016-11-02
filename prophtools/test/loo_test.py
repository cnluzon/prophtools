# -*- coding: utf-8 -*-

import unittest
import os
import prophtools.stats.loo as loo
import tempfile
import shutil
import prophtools.utils.loggingtools as loggingtools
import sys
import StringIO
import mock
from prophtools.common.method import ProphNet
from prophtools.common.graphdata import GraphDataSet
from prophtools.stats.metrics import PrioritizationTest

class TestLOOExperimentFunctions(unittest.TestCase):
    """
    Test for looExperiment class
    """

    def setUp(self):
        config_test_data = """
[cross]
data_path = .
extreme = False
cross =
corr_function = pearson
matfile =
src =
dst =
out = stats

"""
        self.tempdir = tempfile.mkdtemp()
        self.configname = 'config.cfg'
        fo = open(os.path.join(self.tempdir, self.configname), 'w')
        fo.write(config_test_data)
        fo.close()

        fo = open(os.path.join(self.tempdir, 'mockmat.mat'), 'w')
        fo.close()

        tmp_log = os.path.join(self.tempdir, 'loo.log')
        self.log = loggingtools.init_generic_log(tmp_log, 2)

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.tempdir)

    def test_required_parameters_missing_returns_without_running(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = loo.LOOExperiment(cfg_path, 'cross', self.log, section_name='cross')

        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run([], self.configname)
        os.remove('cross.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)

    @mock.patch.object(GraphDataSet, 'read')
    @mock.patch.object(ProphNet, 'propagate')
    @mock.patch.object(PrioritizationTest, 'run_cross_validation')
    def test_required_parameters_required(self, mock_run_cross_validation, mock_propagate, mock_read):
        cfg_path = os.path.join(self.tempdir, self.configname)
        
        exp = loo.LOOExperiment(cfg_path, 'cross', self.log, section_name='cross')
        matfile = os.path.join(self.tempdir, 'mockmat.mat')

        parameters = ['--query', '1', '--src', '0', '--dst', '1', '--matfile', matfile]
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('cross.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        mock_read.assert_called_with('.', matfile)
        mock_propagate.assert_called()
        mock_run_cross_validation.assert_called_with(0,
                                                     1,
                                                     fold=5,
                                                     corr_function='pearson',
                                                     out='stats')
        
        self.assertEqual(result, 0)

    def test_required_not_valid_cross_returns_without_running(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = loo.LOOExperiment(cfg_path, 'cross', self.log, section_name='cross')

        parameters = ['--query', '1', '--src', '0', '--dst', '1', '--matfile', 'test.mat', '--cross', '1']
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('cross.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)

    def test_required_parameters_non_existing_file_returns_without_running(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = loo.LOOExperiment(cfg_path, 'cross', self.log, section_name='cross')

        parameters = ['--query', '1', '--src', '0', '--dst', '1', '--matfile', 'test.mat']
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('cross.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestLOOExperimentFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
