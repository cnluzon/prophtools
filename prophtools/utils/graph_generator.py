# -*- coding: utf-8 -*-

"""
Prophtools: Tools for heterogenoeus network prioritization.

Copyright (C) 2016 Carmen Navarro Luzón <cnluzon@decsai.ugr.es> GPLv3

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Generating random network configurations example.

.. module :: graph_generator.py
.. author :: C. Navarro Luzón <cnluzon@decsai.ugr.es>

"""
import argparse
import networkx as nx
import networkx.algorithms.bipartite as bipartite
import numpy as np

import prophtools.common.graphdata as graphdata

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate a random sample .mat file with a set of three graphs")

    parser.add_argument('-o', '--out', help='.mat file', default="out.mat")

    args = parser.parse_args()

    out_file = args.out

    network_names = ['a', 'b', 'c']
    network_sizes = {'a': 50, 'b': 25, 'c': 20}
    network_densities = {'a': 0.7, 'b': 0.8, 'c': 0.6}

    network_node_names = {}
    networks = {}

    entities = []
    relations = []

    for i in range(len(network_names)):
        nname = network_names[i]
        nsize = network_sizes[nname]
        ndens = network_densities[nname]

        node_name_list = ['{}_{:05d}'.format(nname, i) for i in range(nsize)]
        network_node_names[nname] = node_name_list
        networks[nname] = nx.gnp_random_graph(nsize, ndens)

        entities.append(graphdata.EntityNet.from_raw_matrix(
            nx.to_scipy_sparse_matrix(networks[nname]),
            nname,
            node_name_list))


    relations = []
    bip_graph = bipartite.random_graph(network_sizes['a'], network_sizes['b'], 0.6)
    top_nodes = [n for n,d in bip_graph.nodes(data=True) if d['bipartite'] == 0]
    bip_matrix = bipartite.biadjacency_matrix(bip_graph, top_nodes)
    relations.append(graphdata.RelationNet.from_raw_matrix(bip_matrix, 'rel_ab'))

    bip_graph = bipartite.random_graph(network_sizes['b'], network_sizes['c'], 0.6)
    top_nodes = [n for n,d in bip_graph.nodes(data=True) if d['bipartite'] == 0]
    bip_matrix = bipartite.biadjacency_matrix(bip_graph, top_nodes)
    relations.append(graphdata.RelationNet.from_raw_matrix(bip_matrix, 'rel_bc'))

    bip_graph = bipartite.random_graph(network_sizes['a'], network_sizes['c'], 0.6)

    top_nodes = [n for n,d in bip_graph.nodes(data=True) if d['bipartite'] == 0]
    bip_matrix = bipartite.biadjacency_matrix(bip_graph, top_nodes)
    relations.append(graphdata.RelationNet.from_raw_matrix(bip_matrix, 'rel_ac'))

    connections = np.matrix([[-1, 0, 2], [-1, -1, 1], [-1, -1, -1]])

    dataset = graphdata.GraphDataSet(entities, relations, connections)

    dataset.write('.', args.out)
