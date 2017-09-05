# -*- coding: utf-8 -*-

import unittest
import numpy as np

from prophtools.utils.preprocessing import precompute_matrix, normalize_matrix
import scipy.sparse as sparse

"""
Test for preprocessing methods class.
"""

class TestPreprocessingFunctions(unittest.TestCase):

    def load_test_data(self):
        # symmetric, normal
        self.net_a = np.matrix([[0, 1, 0, 0, 0, 1, 0],
                                [1, 0, 0, 1, 0, 0, 0],
                                [0, 0, 0, 1, 1, 0, 0],
                                [0, 1, 1, 0, 0, 0, 1],
                                [0, 0, 1, 0, 0, 1, 1],
                                [1, 0, 0, 0, 1, 0, 1],
                                [0, 0, 0, 1, 1, 1, 0]])

        # non symmetric, empty row
        self.net_b = np.matrix([[0, 0, 1, 0, 0, 1, 0],
                                [1, 0, 0, 1, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 1, 1, 0, 0, 0, 1],
                                [0, 0, 1, 0, 0, 1, 1],
                                [1, 0, 1, 0, 1, 0, 1],
                                [0, 0, 0, 1, 1, 1, 0]])

        # weighted, asymmetric
        self.net_c = np.matrix([[0, 0, 0, 0.2, 0.8, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0.1, 0, 0, 0, 0, 0.4],
                                [0, 0.01, 0, 0, 0.3, 0, 0.4],
                                [0, 0, 0.3, 0, 0, 0, 0],
                                [0, 0, 0, 0.1, 0, 1, 0],
                                [0.3, 0, 4, 0, 0, 0, 0]])

        self.net_d = np.matrix([[0.00, 0.50, 0.00, 0.00, 0.65, 0.89, 0.00],
                           [0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                           [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
                           [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
                           [0.65, 0.00, 0.00, 0.00, 0.00, 0.00, 2.10],
                           [0.89, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                           [0.00, 0.00, 0.00, 0.00, 2.10, 0.00, 0.00]])

        self.net_d_precomp = [[0.34702097, 0.15462088, 0.        , 0.        , 0.22469187, 0.20628999, 0.1767149 ],
                              [0.15462088, 0.16889387, 0.        , 0.        , 0.10011515, 0.09191589, 0.07873822],
                              [0.        , 0.        , 0.52631579, 0.47368421, 0.        , 0.        , 0.        ],
                              [0.        , 0.        , 0.47368421, 0.52631579, 0.        , 0.        , 0.        ],
                              [0.22469187, 0.10011515, 0.        , 0.        , 0.4076397 , 0.13357027, 0.32059908],
                              [0.20628999, 0.09191589, 0.        , 0.        , 0.13357027, 0.22263109, 0.10504989],
                              [0.1767149 , 0.07873822, 0.        , 0.        , 0.32059909, 0.10504989, 0.35214368]]


        self.python_normalized = normalize_matrix(self.net_a)
        self.python_normalized_twice = normalize_matrix(self.python_normalized)

        self.python_normalized_b = normalize_matrix(self.net_b)

        self.python_normalized_c = normalize_matrix(self.net_c)

    def setUp(self):
        self.load_test_data()

    def tearDown(self):
        """Function to do cleaning up after the test."""

        pass

    def compare_matrices_epsilon(self, a, b, epsilon=0.001):
        for i in range(a.shape[0]):
            for j in range(a.shape[0]):
                if abs(a[i,j] - b[i,j]) > epsilon:
                    return False
        return True

    def test_normalization_twice_not_same_result(self):
        epsilon = 0.001
        normalized = normalize_matrix(self.net_d)
        normalized_twice = normalize_matrix(normalized)

        self.assertFalse(self.compare_matrices_epsilon(normalized,
                                                       normalized_twice,
                                                       epsilon=epsilon))
    def test_normalize_matrix_keeps_dense_result(self):

        normalized = normalize_matrix(self.net_d)
        self.assertFalse(sparse.issparse(normalized))

    def test_normalize_matrix_keeps_sparse_result(self):

        sparse_d = sparse.csr_matrix(self.net_d)
        normalized = normalize_matrix(sparse_d)
        self.assertTrue(sparse.issparse(normalized))

    def test_precompute_matrix_returns_dense_result(self):

        normalized = normalize_matrix(self.net_d)
        precomputed = precompute_matrix(normalized)

        self.assertFalse(sparse.issparse(precomputed))


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPreprocessingFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)