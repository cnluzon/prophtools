# -*- coding: utf-8 -*-

import unittest
import numpy as np

from prophtools.common.graphdata import EntityNet, RelationNet, GraphDataSet
from prophtools.utils.preprocessing import precompute_matrix
from scipy import sparse
import shutil
import tempfile
import mock

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
        self.node_names_b = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5']
        self.net_b = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00]])

        self.net_b_precomp = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89, 0.00],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00, 2.10],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])

        self.rel_ab = np.matrix([
            [0.00, 0.50, 0.00, 0.00, 0.65, 0.89],
            [0.50, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 1.00, 0.00, 0.00],
            [0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
            [0.65, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.89, 0.00, 0.00, 0.00, 0.00, 0.00]])


    def setUp(self):
        self.load_test_data()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.test_dir)

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

    def test_non_matching_names_length_matrix_shape_raises_exception(self):
        with self.assertRaises(ValueError):
            entity = EntityNet(self.net_b,
                               self.name,
                               self.node_names,
                               precomputed=self.net_b_precomp)

    def test_non_squared_matrix_shape_raises_exception(self):
        with self.assertRaises(ValueError):
            entity = EntityNet(self.rel_ab,
                               self.name,
                               self.node_names,
                               precomputed=self.net_b_precomp)


    def test_dims_difference_precomputed_matrix_raise_exception(self):
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

    def test_subset_relation(self):
        r = RelationNet(self.rel_ab, "Relation")
        subset = r.subset([1, 2], [0, 1], precompute=False)

        self.assertEqual(subset.matrix[0, 0], 0.50)
        self.assertEqual(subset.matrix[0, 1], 0.00)

        self.assertEqual(subset.matrix.shape, (2, 2))


    @mock.patch('prophtools.utils.preprocessing.precompute_matrix')
    @mock.patch('prophtools.common.graphdata.EntityNet')
    def test_subset_nodes_precompute_calls_precompute(self, mock_entity_init, mock_precompute_matrix):
        a = EntityNet(self.net_a,
                      self.name,
                      self.node_names,
                      precomputed=self.net_a_precomp)

        subset = a.subset([1, 2], precompute=True)
        mock_precompute_matrix.assert_called()
        mock_entity_init.assert_called()


    def test_relation_net_from_raw_no_errors(self):
        r = RelationNet(self.rel_ab, "Relation")

    def test_relation_net_densify_leaves_dense_matrix_dense(self):
        r = RelationNet(self.rel_ab, "Relation")
        r.densify()

        self.assertEqual(type(r.matrix), np.matrix)

    def test_relation_net_densify_makes_sparse_matrix_dense(self):
        sp = sparse.csr_matrix(self.rel_ab)
        self.assertTrue(sparse.issparse(sp))
        r = RelationNet(sp, "Relation")
        r.densify()
        self.assertEqual(type(r.matrix), np.matrix)

    def test_is_sparse_returns_true_for_csr_matrix(self):
        sp = sparse.csr_matrix(self.rel_ab)
        r = RelationNet(sp, "Relation")
        self.assertTrue(r.is_sparse())

    def test_is_sparse_returns_false_for_numpy_matrix(self):
        r = RelationNet(self.rel_ab, "Relation")
        self.assertFalse(r.is_sparse())

    def test_transpose_does_not_change_object_matrix_shape(self):
        r = RelationNet(self.rel_ab, "Relation")
        shape_before = r.matrix.shape
        transposed = r.transpose()
        shape_after = r.matrix.shape

        self.assertEqual(shape_before, shape_after)

    def test_transpose_returns_a_transposed_relation_net(self):
        r = RelationNet(self.rel_ab, "Relation")
        shape_before = r.matrix.shape
        transposed = r.transpose()
        shape_after = r.matrix.shape

        self.assertNotEqual(shape_before, transposed.matrix.shape)
    
    def test_entity_net_from_raw_no_errors(self):
        e = EntityNet.from_raw_matrix(self.net_a, 'Net', self.node_names)

    def test_entity_net_from_raw_non_squared_raises_exception(self):
        with self.assertRaises(ValueError):
            e = EntityNet.from_raw_matrix(self.rel_ab, 'Net', self.node_names)

    def test_entity_net_is_sparse_returns_false_for_numpy_matrix(self):
        e = EntityNet(self.net_a, 'Net', self.node_names,
                      precomputed=self.net_a_precomp)

        self.assertFalse(e.is_sparse())

    def test_entity_net_is_sparse_returns_true_for_csr_matrix(self):
        sp = sparse.csr_matrix(self.net_a)
        e = EntityNet(sp, 'Net', self.node_names,
                      precomputed=self.net_a_precomp)

        self.assertTrue(e.is_sparse())

    def _create_good_graphdataset(self):
        ent_a = EntityNet(self.net_a, "net_a", self.node_names, self.net_a_precomp)
        ent_b = EntityNet(self.net_b, "net_b", self.node_names_b, self.net_b_precomp)
        rel = RelationNet.from_raw_matrix(self.rel_ab, "rel_ab")
        connections = np.matrix([[-1, 0], [-1, -1]])

        dataset = GraphDataSet([ent_a, ent_b], [rel], connections)
        return dataset

    def test_good_values_graphdataset_raises_no_exception(self):
        self._create_good_graphdataset()

    def test_graphdataset_set_matrix_good_values(self):
        dataset = self._create_good_graphdataset()
        matrix_before = dataset.relations[0].matrix
        dataset.set_relation_matrix(0, 1, matrix_before)

        matrix_after = dataset.relations[0].matrix
        self.assertEqual(matrix_before.shape, matrix_after.shape)

    def test_graphdataset_set_matrix_not_connected_raises_value_error(self):
        dataset = self._create_good_graphdataset()
        dataset.super_adjacency = np.matrix([[0, 0], [0, 0]])
        with self.assertRaises(ValueError):
            dataset.set_relation_matrix(0, 1, self.rel_ab)

    def test_graphdataset_set_matrix_connected_reverse_transposes_matrix(self):
        dataset = self._create_good_graphdataset()
        transposed = np.transpose(self.rel_ab)

        self.assertEqual(transposed.shape[0], self.rel_ab.shape[1])
        self.assertEqual(transposed.shape[1], self.rel_ab.shape[0])

        dataset.set_relation_matrix(1, 0, transposed)

        self.assertEqual(dataset.relations[0].matrix.shape[0], self.rel_ab.shape[0])
        self.assertEqual(dataset.relations[0].matrix.shape[1], self.rel_ab.shape[1])


    def test_read_write_consistency(self):
        matfile = 'testmat.mat'
        ent_a = EntityNet(self.net_a, "net_a", self.node_names, self.net_a_precomp)
        ent_b = EntityNet(self.net_b, "net_b", self.node_names_b, self.net_b_precomp)
        rel = RelationNet.from_raw_matrix(self.rel_ab, "rel_ab")
        connections = np.matrix([[-1, 0], [-1, -1]])
        dataset = GraphDataSet([ent_a, ent_b], [rel], connections)

        dataset.write(self.test_dir, matfile)
        new_dataset = GraphDataSet.read(self.test_dir, matfile)

        self.assertEqual(len(new_dataset.networks), len(dataset.networks))
        self.assertEqual(len(new_dataset.relations), len(dataset.relations))
        self.assertEqual(new_dataset.connections.shape, dataset.connections.shape)

    def test_graphdataset_densify_generates_dense_matrices(self):
        ent_a = EntityNet(self.net_a, "net_a", self.node_names, self.net_a_precomp)
        ent_b = EntityNet(self.net_b, "net_b", self.node_names_b, self.net_b_precomp)
        rel = RelationNet.from_raw_matrix(self.rel_ab, "rel_ab")
        connections = np.matrix([[-1, 0], [-1, -1]])

        dataset = GraphDataSet([ent_a, ent_b], [rel], connections, densify=True)

        self.assertFalse(sparse.issparse(dataset.networks[0].matrix))
        self.assertFalse(sparse.issparse(dataset.networks[1].matrix))
        self.assertFalse(sparse.issparse(dataset.relations[0].matrix))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEntityNetFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)