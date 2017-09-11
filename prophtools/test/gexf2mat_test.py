# -*- coding: utf-8 -*-

import unittest
import os
import prophtools.operations.preprocessxml as preprocessxml
import tempfile
import shutil
import prophtools.utils.loggingtools as loggingtools
import sys
import StringIO
import mock
from prophtools.common.method import ProphNet
from prophtools.common.graphdata import GraphDataSet
import prophtools.utils.graphio  as graphio

class TestPreprocessXMLExperimentFunctions(unittest.TestCase):

    def setUp(self):
        config_test_data = """
[build_matrices]
data_path = .
precompute = True
file =
format = gexf 
labels_as_ids = False
out =
"""
        self.tempdir = tempfile.mkdtemp()
        self.configname = 'build_matrices.cfg'
        fo = open(os.path.join(self.tempdir, self.configname), 'w')
        fo.write(config_test_data)
        fo.close()

        fo = open(os.path.join(self.tempdir, 'mock.gexf'), 'w')
        fo.close()

        self.mock_file = os.path.join(self.tempdir, 'mock.gexf')

        tmp_log = os.path.join(self.tempdir, 'preprocessxml.log')
        self.log = loggingtools.init_generic_log(tmp_log, 2)

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.tempdir)

    def test_required_parameters_missing_returns_without_preprocessing(self):
        cfg_path = os.path.join(self.tempdir, self.configname)
        exp = preprocessxml.PreprocessXMLExperiment(cfg_path, 'build_matrices', self.log, section_name='build_matrices')

        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run([], self.configname)
        os.remove('build_matrices.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        self.assertEqual(result, -1)

    @mock.patch.object(graphio, 'load_graph')
    @mock.patch.object(graphio, 'convert_to_graphdataset')
    @mock.patch.object(GraphDataSet, 'write')
    def test_required_parameters_required(self, mock_write, mock_convert, mock_load):
        cfg_path = os.path.join(self.tempdir, self.configname)
        
        exp = preprocessxml.PreprocessXMLExperiment(cfg_path, 'build_matrices', self.log, section_name='build_matrices')
        matfile = os.path.join(self.tempdir, 'mockmat.mat')

        parameters = ['--file', self.mock_file, '--out', 'test.mat', '--precompute', 'True']
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = exp.run(parameters, self.configname)
        os.remove('build_matrices.cfg')
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        mock_load.assert_called_with(self.mock_file, format="gexf")
        mock_convert.assert_called()
        mock_load.assert_called()
        
        self.assertEqual(result, 0)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPreprocessXMLExperimentFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
