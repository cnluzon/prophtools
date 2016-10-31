# -*- coding: UTF-8 -*-

"""
Prophtools: Tools for heterogenoeus network prioritization.

Copyright (C) 2016 C. Navarro Luzón, V. Martínez Gómez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

.. module :: method.py
.. moduleauthor :: C. Navarro Luzón, V. Martínez Gómez
"""

from __future__ import division

import math
import networkx as nx
import numpy as np

import scipy.sparse as sparse
from scipy.linalg.blas import dgemm
from scipy.stats import pearsonr, spearmanr


# Performs Random Walk with Restarts
# F is the query vector, C_H the adjacency matrix
def RWR(F, C_H, alpha=0.9, maxiter=1000):
    if not sparse.issparse(C_H):
        C_H = sparse.csr_matrix(C_H, dtype=float)

    initial_F = F
    for iter in range(maxiter):
        old_F = F
        F = alpha * C_H * old_F + (1-alpha)*initial_F
        if(abs(F-old_F).sum() < 1e-9):
            break
    return F


class ProphNet:
    def __init__(self, graphdata, method="prophnet"):
        self.graphdata = graphdata
        self.method = method

        self._validate_method(method)

    def _validate_method(self, method):
        implemented_methods = ['prophnet']
        if method.lower() not in implemented_methods:
            msg = "Initialized prophnet with an unknown method: {}".format(method)
            raise ValueError

    @classmethod
    def find_all_paths(cls, graph, start, end):
        """
        Finds all simple paths from start node to end node in a graph.
        Parameters:
            graph:  A networkx.Graph object.
            start:  Start node number.
            end:    End node number.

        Returns: A list of lists of nodes.
        """
        return list(nx.all_simple_paths(graph, start, end))

    def propagate(self, query, src_net, dst_net, corr_function="pearson"):
        """
        Performs propagation on a set of nets. If src_net == dst_net, performs
        single net prioritization.

        Parameters:
            query: Input nodes of the source net (src_net)
            src_net: Source network.
            dst_net: Destination network
            corr_function: "pearson" or "spearman"

        """

        self._validate_query(query, src_net, dst_net)
        scores = None
        if src_net == dst_net:
            scores = self.single_propagation(query,
                                             src_net,
                                             corr_function=corr_function)
        else:
            scores = self.multiple_propagation(query,
                                               src_net,
                                               dst_net,
                                               corr_function=corr_function)

        names = self.graphdata.networks[dst_net].node_names
        tagged_scores = self.associate_scores_to_entities(scores, names)
        return tagged_scores

    def _validate_network_index(self, i):
        if i < 0 or i >= len(self.graphdata.networks):
            msg = "Network out of bounds: {}. Data only has {} nets".format(
                str(i),
                str(len(self.graphdata.networks)))

            raise ValueError(msg)

    def _validate_query_bounds(self, query, i):
        maxquery = max(query)
        minquery = min(query)
        matrix = self.graphdata.networks[i].matrix
        if maxquery >= matrix.shape[0] or minquery < 0:
            msg = "Query out of network bounds: [min:max] [{}:{}] for matrix dims {}".format(
                str(minquery), str(maxquery), str(matrix.shape))
            raise ValueError(msg)

    def _validate_query(self, query, src_net, dst_net):
        self._validate_network_index(src_net)
        self._validate_network_index(dst_net)
        self._validate_query_bounds(query, src_net)

    def _get_correlation_method(self, method_name):
        corr_method = None
        if method_name.lower() == "pearson":
            corr_method = pearsonr
        elif method_name.lower() == "spearman":
            corr_method = spearmanr
        else:
            msg = "Invalid correlation method: {}".format(method_name)
            raise ValueError(msg)

        return corr_method

    def multiple_propagation(self, query, src_net, dst_net,
                             method="prophnet",
                             corr_function="pearson"):

        prioritization_method = RWR
        network_list = [n.matrix for n in self.graphdata.networks]

        corr_method = self._get_correlation_method(corr_function)

        return self._multiple_propagation(query,
                                          src_net,
                                          dst_net,
                                          prioritization_method,
                                          network_list,
                                          corr_function=corr_method)

    def generate_query_vector(self, query, network_index):
        query_vector = np.zeros(self.graphdata.networks[network_index].matrix.shape[0])
        for q in query:
            query_vector[q] = 1.0/len(query)

        return query_vector

    def associate_scores_to_entities(self, scores, names):
        result = []
        if len(scores) != len(names):
            msg = "Scores and names must have the same length: {}, {}".format(
                len(scores), len(names))

            raise ValueError(msg)

        for i in range(len(scores)):
            result.append([scores[i], names[i]])

        return result

    def single_propagation(self, query, src_net, corr_function=None):
        network = self.graphdata.networks[src_net].matrix
        names = self.graphdata.networks[src_net].node_names
        query_vector = self.generate_query_vector(query, src_net)
        initial_score = RWR(query_vector, network)

        vectors = initial_score.tolist()

        corr_method = self._get_correlation_method(corr_function)
        d_vectors = dgemm(alpha=1., a=vectors, b=vectors, trans_a=True)[0][0]
        n_paths = 1

        corr_score = self.compute_correlation_scores(network,
                                                     vectors,
                                                     d_vectors,
                                                     src_net,
                                                     n_paths,
                                                     corr_method)

        return corr_score

    def across_network_propagation(self, network, connection, raise_to_one=False):
        tmp_scores = np.zeros(network.shape[0])
        sum_value = 0
        count_value = 0
        percent = 0.00375

        result = ProphNet.check_matrix_dimensions(connection, network)
        if result != 0:
            msg = "Inner problem with get connection: dimensions do not match."
            raise ValueError(msg)

        for j in range(network.shape[0]):
            column = connection[:, j]
            sum_value = column.sum()
            count_value = column.getnnz()

            if count_value > 0:
                tmp_scores[j] = sum_value/float(count_value)

        # Network inside values propagation and remove noise
        sorted_indices = np.argsort(tmp_scores)[::-1]
        sorted_tmp_scores = tmp_scores[sorted_indices]
        threshold_index = int(math.ceil(percent*tmp_scores.shape[0]))
        sorted_tmp_scores[threshold_index:tmp_scores.shape[0]] = 0.0

        if raise_to_one:
            sorted_tmp_scores[0:threshold_index] = 1.0

        tmp_scores[sorted_indices] = sorted_tmp_scores

        if not raise_to_one:
            tmp_scores = tmp_scores/sum(tmp_scores)

        return tmp_scores

    @classmethod
    def check_matrix_dimensions(cls, matrix_left, matrix_right):
        result = 0  # matched
        if matrix_left.shape[1] != matrix_right.shape[0]:
            if matrix_left.shape[0] != matrix_right.shape[0]:
                result = -1
            else:
                result = 1  # matchable
        return result

    @classmethod
    def match_matrix_dimensions(cls, matrix_left, matrix_right):
        """
        Try to match left matrix (matrix_a) to the dimensions of matrix_b.
        Assumes matrix_b is a square matrix, therefore only makes sense to
        try to match transposing matrix_a.

        Returns:
            The matching left matrix (transposed or not depending what was
            necessary.)

        Raises:
            ValueError if matrices do not match.
        """
        result = ProphNet.check_matrix_dimensions(matrix_left, matrix_right)
        if result == -1:
            msg = "Dimensions connect{}) to net({}) do not match".format(
                str(matrix_left.shape),
                str(matrix_right.shape))
            raise ValueError(msg)
        elif result == 1:
            matrix_left = np.transpose(matrix_left)

        return matrix_left

    def _multiple_propagation(self,
                              query,
                              src_net,
                              dst_net,
                              within_propagation_method=RWR,
                              network_list=None,
                              corr_function=pearsonr):
        """
        Core function for propagation across networks.

        Arguments:
            query: List of indices of the entities of src_net in the query.
            src_net: Index of src_net in network_list.
            dst_net: Index of dst_net in network_list.
            within_propagation_method: A function that takes two parameters:
                a score list for each element in the network and an adjacency
                matrix. Returns a score list for each element in the network
                after propagation.

                Right now it can take RWR as implemented for Prophnet.
            network_list: Adjacency matrix list.
            corr_function: Correlation function used to compute final scores.
                Right now it can be pearsonr or spearmanr from numpy.
        """
        vectors = []
        initial_net = network_list[src_net]
        query_vector = self.generate_query_vector(query, src_net)
        initial_score = within_propagation_method(query_vector, initial_net)
        path_list = ProphNet.find_all_paths(nx.from_numpy_matrix(
                                            self.graphdata.super_adjacency),
                                            src_net,
                                            dst_net)

        for path in path_list:
            current_score = initial_score
            if len(path) > 2:
                for idx, step in enumerate(path[1:-1]):
                    network = network_list[path[idx+1]]
                    prev_net = path[idx]
                    current_net = path[idx+1]

                    connection = self.graphdata.get_connection(prev_net,
                                                               current_net)

                    tmp_scores = self.across_network_propagation(network,
                                                                 connection.matrix)
                    current_score = within_propagation_method(tmp_scores, network)

            connection = self.graphdata.get_connection(path[-2], dst_net).matrix
            connection = self.match_matrix_dimensions(connection, current_score)

            if len(current_score.shape) == 1:
                new_shape = (current_score.shape[0], 1)
                current_score = np.reshape(current_score, new_shape)

            compu = (connection * current_score).tolist()
            vectors += compu

        d_vectors = dgemm(alpha=1., a=vectors, b=vectors, trans_a=True)[0][0]
        dst_net_matrix = network_list[dst_net]

        return self.compute_correlation_scores(dst_net_matrix,
                                               vectors,
                                               d_vectors,
                                               dst_net,
                                               len(path_list),
                                               corr_function)

    def compute_correlation_scores(self,
                                   network,
                                   vectors,
                                   d_vectors,
                                   dst_net_index,
                                   n_paths,
                                   corr_function):

        horizontal_vectors = np.ravel(vectors)
        corr_results = np.zeros(network.shape[0], dtype='f,f')
        corr_scores = np.zeros(network.shape[0])

        if sum(horizontal_vectors) > 0:
            for i in range(network.shape[0]):
                current_row = self.graphdata.networks[dst_net_index].precomputed[i]
                if sparse.issparse(current_row):
                    current_row = np.ravel(current_row.todense())

                final_net = np.tile(current_row, n_paths)
                score_tuple = corr_function(horizontal_vectors, final_net)
                corr_results[i] = score_tuple
                corr_scores[i] = score_tuple[0]
        else:
            msg = ("Warning: Propagation resulted in an all-zero vectors, which"
                   " cannot be correlated to the scores.")
            print msg
            return None

        return corr_scores
