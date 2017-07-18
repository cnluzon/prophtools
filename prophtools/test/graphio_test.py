# -*- coding: utf-8 -*-

import unittest
import numpy as np
from prophtools.utils import graphio

from prophtools.common.graphdata import EntityNet, RelationNet, GraphDataSet
from prophtools.utils.preprocessing import precompute_matrix
from scipy import sparse
import shutil
import tempfile
import mock

class TestGraphIOFunctions(unittest.TestCase):
    def test_load_graph_non_existing_file_raises_exception(self):
        with self.assertRaises(IOError):
            non_existing_filename = '_'
            graphio.load_graph(non_existing_filename)


    def test_load_graph_unknown_format_raises_exception(self):
        with self.assertRaises(TypeError):
            existing_filename = "_"
            unknown_format = "unknown"
            graphio.load_graph(existing_filename, unknown_format)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraphIOFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)