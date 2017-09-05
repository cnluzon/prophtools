# -*- coding: latin-1 -*-

"""
 .. module :: graphdata.py
 .. moduleauthor :: C. Navarro Luzón

 Encapsulates data for the whole network structure to propagate.
 Includes I/O functions to .mat files.

"""

import os

import scipy.io as sio
import numpy as np

from scipy.linalg.blas import dgemm
from scipy import sparse
import shutil
import sys
import prophtools.utils.preprocessing as preprocessing
import random
from tempfile import mkdtemp

class RelationNet:
    """Models a relationship between two different networks. This means it
       models a bipartite graph, in the form of a non-symmetric matrix.
    Args:
        matrix - A non symmetric normalized numpy/scipy sparse matrix.
        net_name - String.
    """

    def __init__(self, matrix, net_name):
        self.matrix = matrix
        self.name = net_name

    @classmethod
    def from_raw_matrix(cls, matrix, net_name):
        """
        Creates a RelationNet object considering it raw: i.e. normalizes first.
        """
        normalized_matrix = preprocessing.normalize_matrix(matrix)
        return cls(normalized_matrix, net_name)

    def densify(self):
        if self.is_sparse():
            self.matrix = self.matrix.todense()

    def subset(self, row_list, column_list, normalize=False, precompute=True):
        new_matrix = self.matrix[row_list, :][:, column_list]
        if normalize:
            new_matrix_norm = preprocessing.normalize_matrix(new_matrix)
            new_matrix = new_matrix_norm

        return RelationNet(new_matrix, self.name)

    def is_sparse(self):
        return sparse.issparse(self.matrix)

    def transpose(self):
        # new_mat = np.transpose(self.matrix)
        new_mat = self.matrix.transpose()
        return RelationNet(new_mat, self.name)


class EntityNet:
    """
    Models a network of interconected entities of any nature. The relations
    between the entities are symmetric (i.e the value of the relationship
    between A and B is the same as the value of the relationship between
    B and A.).

    Args:
        matrix: Symmetric and square adjacency matrix for the nodes.
        name  : Name of the network.
        node_names: Names of the nodes in the network.
        precomputed: Precomputed values (used for correlation speed-up).

    length(node_names) must match shape of the network (i.e. each node is
    named.)

    shape of precomputed matrix and adjacency matrix must match.
    """

    def __init__(self, matrix, net_name, node_names, precomputed=None):
        self.matrix = matrix
        self.name = net_name
        self.node_names = node_names
        self.precomputed = precomputed

        self._validate_dimensions()
        # self.precompute_dot_values()

    @classmethod
    def from_raw_matrix(cls, matrix, net_name, node_names):
        """
        Creates an EntityNet object considering it raw: i.e. normalizes first
        and builds precomputed matrix.

        Warning: precomputing a matrix is time consuming. However, it is
        necessary for propagation methods to work.
        """
        norm_matrix = preprocessing.normalize_matrix(matrix)
        norm_prec_matrix = preprocessing.precompute_matrix(norm_matrix)

        return cls(norm_matrix, net_name, node_names,
                   precomputed=norm_prec_matrix)

    def _validate_dimensions(self):
        self._check_matrix_squared()
        self._check_names_match_matrix()
        self._check_matrix_matches_precomputed()

    def _check_names_match_matrix(self):
        if len(self.node_names) != self.matrix.shape[0]:
            msg = "Matrix dims and node names list dont match ({},{})".format(
                len(self.node_names), self.matrix.shape[0])
            raise ValueError(msg)

    def _check_matrix_matches_precomputed(self):
        if self.precomputed is not None:
            if self.matrix.shape[0] != self.precomputed.shape[0]:
                msg = "Precomp. matrix and entity matrix dims do not match."
                raise ValueError(msg)

    def _check_matrix_squared(self):
        if self.matrix.shape[0] != self.matrix.shape[1]:
            msg = "An entity matrix should be squared. Dimensions: {}".format(
                str(self.matrix.shape))
            raise ValueError(msg)

    def is_sparse(self):
        sparse_types = [sparse.csr_matrix, sparse.csc_matrix]
        return type(self.matrix) in sparse_types

    def densify(self):
        if self.precomputed is not None and sparse.issparse(self.precomputed):
                self.precomputed = np.asarray(self.precomputed.todense())

        if self.is_sparse():
            self.matrix = self.matrix.todense()

    def subset(self, node_list, precompute=True):
        """
        Generate a network that contains a subset of the nodes.

        Args:
            node_list: List of integers to retrieve.
            precompute: Whether or not to generate a precomputed matrix.
                WARNING: This is very time consuming if the net is big.
                WARNING: Perform this on RAW matrices, THEN normalize.
                         Normalizing twice causes error.

        Returns:
            A new, reduced EntityNet.
        """
        reduced_matrix = self.matrix[node_list, :][:, node_list]
        reduced_names = [self.node_names[i] for i in node_list]
        precomputed = None

        if precompute:
            normalized_reduced_matrix = preprocessing.normalize_matrix(
                reduced_matrix)
            precomputed = preprocessing.precompute_matrix(
                normalized_reduced_matrix)

        return EntityNet(reduced_matrix,
                         self.name,
                         reduced_names,
                         precomputed=precomputed)


class GraphDataSet:
    """
    Encapsulates data for the whole network structure to propagate, including
    Entity networks, relation networks modelling connections between entities
    and information about which relation networks connect which entities,
    i.e. a super-adjacency matrix.

    Args:
        networks:    A list of EntityNet objects.
        relations:   A list of RelationNet objects.
        connections: A square np.matrix of shape len(networks), and whose
                       numbers are not higher than len(relations).
                     If networks i, j are not connected, connections[i,j]==-1
                     connections represents a DIRECTED graph, to keep
                     data consistency. connections[i,j]==a means relations[a]
                     models such connection, but in a way that rows are
                     entities of networks[i] and cols entities of networks[j].
                     connections[j,i] should be -1.
        densify:     convert matrices to dense matrices. This is not recommended,
                     consumes a lot of memory. False by default.
    """
    def __init__(self, networks, relations, connections, densify=False, tmpdir=None):

        self.networks = networks
        self.relations = relations
        self.connections = connections
        self.connection_edges = self.compute_connection_edges(connections)
        self.super_adjacency = self.compute_super_adjacency(connections)
        self.is_dense = False
        self.tmpdir = tmpdir

        self._check_consistent_types()

        if densify:
            self.densify()

    def cleanup_resources(self):
        if self.tmpdir:
            try:
                shutil.rmtree(self.tmpdir)
            except:
                print "Unexpected error deleting tmp file:", sys.exc_info()
                print self.tmpdir

    @staticmethod
    # @profile
    def _extract_nets_from_data_dictionary(data, memsave=False):
        network_names = data['entities']
        network_names = [n.rstrip().encode("utf8") for n in network_names]
        relation_names = data['relations']
        relation_names = [n.rstrip().encode("utf8") for n in relation_names]
        connections = data['connections']

        relation_nets = []
        entity_nets = []

        tmpdir = None
        if memsave:
            tmpdir = mkdtemp()

        for name in network_names:
            precomputed_mat = data.get("{}_precomputed".format(name), None)
            if memsave:
                filename = os.path.join(tmpdir, '{}_precomp.dat'.format(name))
                precomputed_memmap = np.memmap(filename, dtype='float32', mode='w+', shape=precomputed_mat.shape)
                precomputed_memmap[:] = precomputed_mat[:]
                precomputed_mat = precomputed_memmap

            new_net = EntityNet(data[name],
                                name,
                                data['{}_name'.format(name)],
                                precomputed=precomputed_mat)

            entity_nets.append(new_net)

        for name in relation_names:
            new_relation = RelationNet(data[name], name)
            relation_nets.append(new_relation)

        return [entity_nets, relation_nets, connections, tmpdir]

    @classmethod
    # @profile
    def read(cls, data_path, data_file, memsave=False):
        """
        Loads network data.

        Assumes these matrices are normalized and there are precomputed
        matrices as well, and that the names are followed by "_name" and
        "_precomputed" to indicate which data the entities contain.
        """
        data = sio.loadmat(os.path.join(data_path, data_file))

        entity_nets, relation_nets, connections, tmpdir = GraphDataSet._extract_nets_from_data_dictionary(data, memsave=memsave)

        return cls(entity_nets, relation_nets, connections, densify=False, tmpdir=tmpdir)

    def get_relation_matrix(self, origin, destination):
        return self.relations[self.connections[origin, destination]].matrix

    def set_relation_matrix(self, src, dst, new_matrix):
        connected = self.super_adjacency[src, dst]
        if connected:
            rel_index = self.connections[src, dst]
            if rel_index != -1:
                self._set_matrix(rel_index, new_matrix)

            else:   # connections must be
                rel_index = self.connections[dst, src]
                self._set_matrix(rel_index, new_matrix)

        else:
            msg = "Non-connected {} and {}".format(src, dst)
            raise ValueError(msg)

    def _set_matrix(self, rel_index, new_matrix):
        old_shape = self.relations[rel_index].matrix.shape
        new_shape = new_matrix.shape
        if old_shape == new_shape:
            self.relations[rel_index].matrix = new_matrix
        elif old_shape[1] == new_shape[0] and old_shape[0] == new_shape[1]:
            self.relations[rel_index].matrix = new_matrix.transpose()
        else:
            msg = "Incompatible dims: {}, {}".format(new_shape, old_shape)
            raise ValueError(msg)

    def _check_consistent_types(self):
        first_type = self.networks[0].is_sparse()
        for n in self.networks[1:]:
            if n.is_sparse() != first_type:
                msg = "Inconsistent types, some sparse some not!"
                raise ValueError(msg)

        first_type = self.relations[0].is_sparse()
        for r in self.relations[1:]:
            if r.is_sparse() != first_type:
                msg = "Inconsistent types, some sparse some not!"
                raise ValueError(msg)

    def write(self, path, filename):
        """
        Write current data to .mat file.
        """
        mdict = {}

        for i in range(len(self.networks)):
            name = self.networks[i].name
            precomputed_name = "{}_precomputed".format(name)
            names_name = "{}_name".format(name)
            mdict[name] = self.networks[i].matrix
            mdict[precomputed_name] = self.networks[i].precomputed
            mdict[names_name] = self.networks[i].node_names

        for i in range(len(self.relations)):
            name = self.relations[i].name
            mdict[name] = self.relations[i].matrix

        mdict['connections'] = self.connections
        mdict['entities'] = [n.name for n in self.networks]
        mdict['relations'] = [r.name for r in self.relations]

        sio.savemat(os.path.join(path, filename), mdict, do_compression=True)

    def densify(self):
        """
        Computes the dense matrices from which to operate from now on where it
        finds a sparse matrix
        """
        if not self.is_dense:
            for n in self.networks:
                n.densify()

            for r in self.relations:
                r.densify()

        self.is_dense = True

    def compute_connection_edges(self, connections_mat):
        """
        Returns a list of tuples where list[i] shows which networks
        relations[i] connects.

        Example: [(1,2), (2,3)]. list[0] = (1,2) means that relations[0]
        links networks[1] with networks[2], where rows are entities of
        networks[1] and columns entities of networks[2]

        Connections mat is expected NOT to be symmetric.
        This means: connections[i,j] = 2
                    relations[2] connects i to j,
                    where i are the ROWS and j the COLUMNS of the relation mat.

                    connections[j, i] would be in this case -1.

                    If relations[2] was transposed, then connections[j, i]
                    would equal to 2 and connections[i,j] to -1.
        """
        result = []
        for i in range(len(self.relations)):
            result.append((-1, -1))

        for i in range(connections_mat.shape[0]):
            for j in range(connections_mat.shape[1]):
                current_mat = connections_mat[i, j]
                if current_mat != -1:
                    result[current_mat] = (i, j)

        return result

    def compute_super_adjacency(self, connections_mat):
        """
        Generates a "super adjacency matrix" where m[i,j] equals to 1 if
        networks i and j are connected, 0 otherwise. It is created from the
        connections matrix, where connections[i,j] is the number of the network
        that connects i and j, -1 if no such network exist.

        Arguments:
            connections_mat: Matrix of integers. m[i,j] connects networks i
                             and j. NON-symmetric.

        Returns:
            a {0,1} symmetric matrix indicating connections between networks.
        """
        result = np.zeros(connections_mat.shape)
        for i in range(connections_mat.shape[0]):
            for j in range(connections_mat.shape[1]):
                if connections_mat[i, j] != -1:
                    result[i, j] = 1
                    result[j, i] = 1

        return result

    def subsample_network(self, matrix, row_list, column_list):
        by_row_matrix = matrix[row_list, :]
        result = by_row_matrix[:, column_list]
        return result

    def subset(self, nodes_list_per_net):
        """
        Extract a subset of the dataset taking the selected nodes in nodes.
        Nodes should be a list of the same length as dataset.networks, where
        for each item, a list of indexes is selected.
        A warning is thrown if gifen the selected nodes, some relations between
        networks are broken.
        """

        n_nets = len(nodes_list_per_net)

        if n_nets != len(self.networks):
            msg = ("nodes_list_per_net should be of the same length as number"
                   " of networks in the dataset.")
            raise ValueError(msg)

        subsampled_nets = []
        subsampled_rels = []

        for i in range(n_nets):
            subsampled_nets.append(self.networks[i].subset(nodes_list_per_net[i]))

        for i in range(len(self.relations)):
            (origin, destination) = self.connection_edges[i]
            new_rel = self.relations[i].subset(nodes_list_per_net[origin],
                                               nodes_list_per_net[destination])
            subsampled_rels.append(new_rel)

        return GraphDataSet(subsampled_nets, subsampled_rels, self.connections)

    def choose_random_nodes(self, random_size):

        for n in self.networks:
            if random_size > n.matrix.shape[0]:
                msg = "Size too big for subsample. Size {}, matrix {}".format(
                    random_size, str(n.matrix.shape))
                raise ValueError(msg)

        node_list_per_net = []
        for n in self.networks:
            index_choices = random.sample(range(n.matrix.shape[0]), random_size)
            node_list_per_net.append(index_choices)

        return node_list_per_net

    def random_subset(self, random_size):

        nodes_list_per_net = self.choose_random_nodes(random_size)
        return self.subset(nodes_list_per_net)

    def get_connection_direction(self, origin, destination):
        """
        Return the direction of the connection. This means whether the matrix
        is forward or reverse considering the origin-destination indices.

        If reverse is obtained, the matrix returned should be transposed.

        Returns:
            1 : Forward connection
            0 : Reverse connection
            -1: No connection

        """
        if self.connections[origin, destination] != -1:
            return 1    # forward
        elif self.connections[destination, origin] != -1:
            return 0    # reverse
        else:
            return -1   # no connection

    def get_connection(self, origin, destination):
        """
        Returns the matrix that connects origin and destination. Returns it
        transposed if necessary.

        Example: if connections[0, 1] = 2, relations[2] connects 0 and 1,
        where rows of relations[2] are entities[0] and columns entities[1].

        get_connection(0, 1) will return relations[2]. get_connection(1,0) will
        return relations[2] transposed.
        """

        if self.super_adjacency[origin, destination] == 0:
            msg = "No connection whatsoever between matrices {} and {}".format(
                origin, destination)
            raise ValueError(msg)

        else:
            connection_index = self.connections[origin, destination]
            if connection_index != -1:
                return self.relations[connection_index]
            else:
                connection_index = self.connections[destination, origin]
                return self.relations[connection_index].transpose()
