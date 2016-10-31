# -*- coding: utf-8 -*-

import unittest
import numpy as np

from prophtools.common.graphdata import EntityNet, RelationNet, GraphDataSet

from scipy import sparse


class TestEntityNetFunctions(unittest.TestCase):
    """
    Test for graphdata module
    """
    def load_test_data(self):
        self.net_a = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89, 0.00],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00, 2.10],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 0.00, 2.10, 0.00, 0.00]])

        self.net_a_precomp = np.matrix([
            [0.34,  0.15,  0.00, 0.00, 0.22, 0.20,  0.17],
            [0.15,  0.17,  0.00, 0.00, 0.10, 0.09,  0.07],
            [0.00,  0.00,  0.52, 0.47, 0.00, 0.00,  0.00],
            [0.00,  0.00,  0.47, 0.52, 0.00, 0.00,  0.00],
            [0.22,  0.10,  0.00, 0.00, 0.40, 0.13,  0.32],
            [0.20,  0.09,  0.00, 0.00, 0.13, 0.22,  0.10],
            [0.17,  0.07,  0.00, 0.00, 0.32, 0.10,  0.35]])
        self.name = 'net_a'
        self.node_names = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6']

        self.net_b = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89, 0.00],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00, 2.10],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])

        self.net_b_precomp = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89, 0.00],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00, 2.10],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])

    def setUp(self):
        self.load_test_data()

    def tearDown(self):
        """Function to do cleaning up after the test."""

        pass

    def test_densify_keep_dense_matrix(self):
        a_from_raw = EntityNet.from_raw_matrix(self.net_a, self.name, self.node_names)
        type_before = type(a_from_raw.matrix)
        a_from_raw.densify()
        type_after = type(a_from_raw.matrix)
        self.assertEqual(type_before, type_after)

    def test_densify_changes_sparse_matrix_to_dense(self):
        a_from_raw = EntityNet.from_raw_matrix(
            sparse.csr_matrix(self.net_a),
            self.name,
            self.node_names)

        type_before = type(a_from_raw.matrix)
        a_from_raw.densify()
        type_after = type(a_from_raw.matrix)
        self.assertNotEqual(type_before, type_after)

    def test_inconsistency_length_names_matrix_dims_raises_exception(self):
        new_names = ['a0']
        with self.assertRaises(ValueError):
            a_from_raw = EntityNet(self.net_a,
                                   self.name,
                                   new_names,
                                   precomputed=self.net_a_precomp)

    def test_non_square_matrix_raises_exception(self):
        with self.assertRaises(ValueError):
            b_from_raw = EntityNet(self.net_b,
                                   self.name,
                                   self.node_names,
                                   precomputed=self.net_b_precomp)

    def test_dims_difference_precomputed_matrix_raise_eception(self):
        with self.assertRaises(ValueError):
            a_from_raw = EntityNet(self.net_a,
                                   self.name,
                                   self.node_names,
                                   precomputed=self.net_b_precomp)

    def test_subset_nodes(self):
        a = EntityNet(self.net_a,
                      self.name,
                      self.node_names,
                      precomputed=self.net_a_precomp)

        subset = a.subset([1, 2], precompute=False)

        self.assertEqual(subset.matrix.shape, (2, 2))
        self.assertEqual(subset.node_names, ['a1', 'a2'])
        self.assertEqual(subset.matrix[0, 0], 0.00)
        self.assertEqual(subset.matrix[0, 1], 0.00)
        self.assertEqual(subset.matrix[1, 0], 0.00)
        self.assertEqual(subset.matrix[1, 1], 0.00)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEntityNetFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)