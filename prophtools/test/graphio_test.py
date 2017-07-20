# -*- coding: utf-8 -*-

import mock
import numpy as np
import networkx as nx
import os
import shutil
import StringIO
import tempfile
import unittest

from prophtools.utils import graphio

class TestGraphIOFunctions(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'temp.gexf')
        self._write_sample_gexf_file(self.test_file)

    def _write_sample_gexf_file(self, filename):
        value = """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <meta lastmodifieddate="2014-01-30">
    <creator>Gephi 0.8.1</creator>
    <description></description>
    </meta>
    <graph defaultedgetype="undirected" mode="static">
        <attributes class="node">
            <attribute id="0" title="group" type="integer"/>
        </attributes>
        <nodes>
            <node id="0" label="Mark Johnson">
                <attvalue for="0" value="0"/>
            </node>
            <node id="1" label="Jane Schwartz">
                <attvalue for="0" value="0"/>
            </node>
            <node id="2" label="Ed Lopez">
                <attvalue for="0" value="1"/>
            </node>
            <node id="3" label="Maria Lopez">
                <attvalue for="0" value="0"/>
            </node>            
        </nodes>

        <edges>
            <edge id="0" source="0" target="1" weight="0.25"/>
            <edge id="1" source="0" target="3" weight="0.88"/>
            <edge id="2" source="2" target="3" weight="1.00"/>
            <edge id="3" source="1" target="2" weight="0.52"/>           
        </edges>

    </graph>
</gexf>
        """
        fo = open(self.test_file, 'w')
        fo.write(value)
        fo.close()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_graph_non_existing_file_raises_exception(self):
        with self.assertRaises(IOError):
            non_existing_filename = '_'
            graphio.load_graph(non_existing_filename, format="GEXF")

    def test_load_graph_unknown_format_raises_exception(self):
        with self.assertRaises(TypeError):
            unknown_format = "unknown"
            graphio.load_graph(self.test_file, format=unknown_format)

    def test_load_graph_gexf_valid_format_runs(self):
        graphio.load_graph(self.test_file, format='GEXF')

    def test_load_graph_gexf_node_number(self):
        graph = graphio.load_graph(self.test_file, format='GEXF')
        self.assertEquals(len(graph.nodes()), 4)

    def test_load_graph_gexf_edge_number(self):
        graph = graphio.load_graph(self.test_file, format='GEXF')
        self.assertEquals(len(graph.edges()), 4)

    def test_load_graph_gexf_undirected_symmetric_adj_matrix(self):
        graph = graphio.load_graph(self.test_file, format='GEXF')
        adj_matrix  = nx.adjacency_matrix(graph).todense()
        for i in range(adj_matrix.shape[0]):
            for j in range(i+1, adj_matrix.shape[1]):
                self.assertEquals(adj_matrix[i,j], adj_matrix[j,i])

    def test_load_graph_gexf_adjacency_matrix(self):
        result = np.matrix([[0,    0.25, 0,    0.88],
                            [0.25, 0,    0.52,    0],
                            [0,    0.52,    0, 1.00],
                            [0.88, 0,    1.00,    0]])

        graph = graphio.load_graph(self.test_file, format='GEXF')
        nodes = graph.nodes()
        adj_matrix = nx.adjacency_matrix(graph).todense()
        
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                result_i = nodes.index(str(i))  # Order of the nodes is not fixed
                result_j = nodes.index(str(j))
                self.assertEquals(adj_matrix[i,j], result[result_i,result_j])

    def test_node_attributes(self):
        graph = graphio.load_graph(self.test_file, format='GEXF')
        node_attributes = nx.get_node_attributes(graph, "0")
        print node_attributes
        self.assertEquals[node_attributes['2']] == '1'

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraphIOFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)