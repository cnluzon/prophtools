# -*- coding: utf-8 -*-

import unittest
import networkx as nx
import numpy as np
import os
from prophtools.common.method import ProphNet
from prophtools.common.graphdata import GraphDataSet


class TestProphNetFunctions(unittest.TestCase):
    """
    Test for ProphNet class
    """
    def load_test_data(self):
        script_dir = os.path.dirname(__file__)
        absolute_path = os.path.join(script_dir, '../matfiles/')
        self.sample_data = GraphDataSet.read(absolute_path, 'example.mat')
        self.sample_data_memsave = GraphDataSet.read(absolute_path, 'example.mat', memsave=True)

        self.prophnet = ProphNet(self.sample_data)
        self.prophnet_memsave = ProphNet(self.sample_data_memsave)

    def setUp(self):
        self.load_test_data()

    def tearDown(self):
        """Function to do cleaning up after the test."""
        self.prophnet_memsave.graphdata.cleanup_resources()

    def test_find_all_paths_normal_case(self):
        super_adjacency = np.matrix('0 1 1; 1 0 1; 1 1 0')
        paths = ProphNet.find_all_paths(nx.from_numpy_matrix(super_adjacency), 0, 2)
        self.assertTrue([0, 2] in paths)
        self.assertTrue([0, 1, 2] in paths)

    def test_find_all_paths_no_connection(self):
        network = nx.from_numpy_matrix(np.matrix('0 0 1; 0 0 0; 1 0 0'))
        paths = ProphNet.find_all_paths(network, 1, 2)
        self.assertEquals([], paths)

    def test_find_all_paths_single_connection(self):
        network = nx.from_numpy_matrix(np.matrix('0 0 1; 0 0 0; 1 0 0'))
        paths = ProphNet.find_all_paths(network, 0, 2)
        self.assertTrue([0, 2] in paths)

    def test_compute_super_adjacency(self):
        adj = self.prophnet.graphdata.super_adjacency

        self.assertEquals(adj[0, 1], 1)
        self.assertEquals(adj[1, 0], 1)
        self.assertEquals(adj[0, 0], 0)
        self.assertEquals(adj[1, 1], 0)

    def test_match_matrix_dimensions_matched(self):
        mat_a = np.matrix('0 1 1; 1 0 1; 1 1 0')
        mat_b = np.matrix('0 0 1; 1 0 1; 1 1 0')
        result = ProphNet.check_matrix_dimensions(mat_a, mat_b)
        self.assertEquals(result, 0)

    def test_match_matrix_dimensions_unmatchable(self):
        mat_a = np.matrix('0 1 1; 1 0 1; 1 1 0')
        mat_b = np.matrix('0 1; 1 0')
        with self.assertRaises(ValueError):
            ProphNet.match_matrix_dimensions(mat_a, mat_b)

    def test_match_matrix_dimensions_matched_non_squared(self):
        mat_a = np.matrix('0 1 1; 1 0 1; 1 1 0')
        mat_b = np.matrix('0 1 0; 0 1 0')
        self.assertEquals(mat_b.shape[0], 2)
        result = ProphNet.match_matrix_dimensions(mat_b, mat_a)
        self.assertEquals(result.shape[0], 2)

    def test_match_matrix_dimensions_matchable(self):
        mat_a = np.matrix('0 1 1; 1 0 1; 1 1 0')
        mat_b = np.matrix('0 1; 0 1; 1 0')
        self.assertEquals(mat_b.shape[0], 3)
        result = ProphNet.match_matrix_dimensions(mat_b, mat_a)
        self.assertEquals(result.shape[0], 2)

    def test_unknown_method_raises_exception(self):
        with self.assertRaises(ValueError):
            ProphNet(self.sample_data, method="not_valid")

    def test_network_out_of_bounds_raises_exception(self):
        with self.assertRaises(ValueError):
            self.prophnet.propagate([3], 0, 5)

    def test_unknown_correlation_function_raises_exception(self):
        with self.assertRaises(ValueError):
            self.prophnet.propagate([3], 0, 1, corr_function="not_valid")

    def test_generate_query_vector_matches_network_length(self):
        query = [3]
        dst = 2
        network_length = self.prophnet.graphdata.networks[dst].matrix.shape[0]

        query_vector = self.prophnet.generate_query_vector(query, dst)
        self.assertEquals(network_length, len(query_vector))

    def _within_network_propagation_best_results_matches_query(self, method, query):
        names = method.graphdata.networks[0].node_names
        scores = method.propagate(query, 0, 0)

        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
        result_tag = sorted_scores[0][1]
        result_index = np.where(names == result_tag)

        return (query[0] == result_index[0])

    def test_within_network_propagation_memsavemode_same_results(self):
        queries = [1, 8, 0]
        for q in queries:
            result_save = self._within_network_propagation_best_results_matches_query(self.prophnet_memsave, [q])
            self.assertTrue(result_save)

    def test_within_network_propagation_best_result_is_query_a(self):
        result = self._within_network_propagation_best_results_matches_query(self.prophnet, [1])
        self.assertTrue(result)

    def test_within_network_propagation_best_result_is_query_b(self):
        result = self._within_network_propagation_best_results_matches_query(self.prophnet, [8])
        self.assertTrue(result)

    def test_within_network_propagation_best_result_is_query_c(self):
        result = self._within_network_propagation_best_results_matches_query(self.prophnet, [0])
        self.assertTrue(result)

    def test_query_out_of_bounds_raises_exception(self):
        names = self.prophnet.graphdata.networks[0].node_names
        query = [len(names)]
        with self.assertRaises(ValueError):
            scores = self.prophnet.propagate(query, 0, 0)

    def _across_network_propagation_dst_names_test(self, method, query, src, dst):
        scores = method.propagate(query, src, dst)
        names_dst = method.graphdata.networks[dst].node_names
        return (scores[0][1] in names_dst)

    def test_across_network_propagation_returns_dst_net_tags_forward(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet, [1], 0, 1)
        self.assertTrue(result)

    def test_across_network_propagation_returns_dst_net_tags_reverse(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet, [1], 1, 0)
        self.assertTrue(result)

    def test_across_network_propagation_returns_dst_net_tags_forward_2(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet, [1], 0, 2)
        self.assertTrue(result)

    def test_across_network_propagation_returns_dst_net_tags_forward_memsave(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet_memsave, [1], 0, 1)
        self.assertTrue(result)

    def test_across_network_propagation_returns_dst_net_tags_reverse_memsave(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet_memsave, [1], 1, 0)
        self.assertTrue(result)

    def test_across_network_propagation_returns_dst_net_tags_forward_2_memsave(self):
        result = self._across_network_propagation_dst_names_test(self.prophnet_memsave, [1], 0, 2)
        self.assertTrue(result)

if __name__ == '__main__':

    # Run the whole test using this function
    # unittest.main()
    # or you can have a more detailed test view with:
    # This will load all the tests methods that start with test_*
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProphNetFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)