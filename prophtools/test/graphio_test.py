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
        self.test_three_group_gexf_file = os.path.join(self.test_dir, 'temp2.gexf')
        self.test_no_attr_file = os.path.join(self.test_dir, 'no_attribute.gexf')

        self.test_missing_attr_file = os.path.join(self.test_dir, 'missing_attr.gexf')
        
        self._write_sample_gexf_file(self.test_file)
        self._write_sample_three_group_gexf_file(self.test_three_group_gexf_file)
        self._write_gexf_file_no_attributes(self.test_no_attr_file)
        self._write_gexf_file_missing_attributes(self.test_missing_attr_file)


    def _write_gexf_file_missing_attributes(self, filename):
        value = """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
<meta lastmodifieddate="2014-01-30">
<creator>Gephi 0.8.1</creator>
<description></description>
</meta>
<graph defaultedgetype="undirected" mode="static">
    <attributes class="node">
        <attribute id="0" title="group" type="integer"/>    
        <attribute id="1" title="other" type="integer"/>
    </attributes>
    <nodes>
        <node id="0" label="Mark Johnson">
            <attvalue for="1" value="0"/>
        </node>
        <node id="1" label="Jane Schwartz">
            <attvalue for="0" value="0"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="2" label="Ed Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="3" label="Maria Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
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
        fo = open(filename, 'w')
        fo.write(value)
        fo.close()


    def _write_gexf_file_no_attributes(self, filename):
        value = """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
<meta lastmodifieddate="2014-01-30">
<creator>Gephi 0.8.1</creator>
<description></description>
</meta>
<graph defaultedgetype="undirected" mode="static">
    <attributes class="node">
        <attribute id="1" title="other" type="integer"/>
        <attribute id="2" title="pepe" type="integer"/>
    </attributes>
    <nodes>
        <node id="0" label="Mark Johnson">
            <attvalue for="0" value="0"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="1" label="Jane Schwartz">
            <attvalue for="0" value="0"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="2" label="Ed Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="3" label="Maria Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
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
        fo = open(filename, 'w')
        fo.write(value)
        fo.close()


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
        <attribute id="1" title="other" type="integer"/>
    </attributes>
    <nodes>
        <node id="0" label="Mark Johnson">
            <attvalue for="0" value="0"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="1" label="Jane Schwartz">
            <attvalue for="0" value="0"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="2" label="Ed Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
        </node>
        <node id="3" label="Maria Lopez">
            <attvalue for="0" value="1"/>
            <attvalue for="1" value="0"/>
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
        fo = open(filename, 'w')
        fo.write(value)
        fo.close()


    def _write_sample_three_group_gexf_file(self, filename):
        value =  """<?xml version="1.0" encoding="UTF-8"?>
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
        <node id="0" label="0_group_0">
            <attvalue for="0" value="0"/>
        </node>
        <node id="1" label="1_group_0">
            <attvalue for="0" value="0"/>
        </node>
        <node id="2" label="2_group_0">
            <attvalue for="0" value="0"/>
        </node>
        <node id="3" label="3_group_1">
            <attvalue for="0" value="1"/>
        </node>     
        <node id="4" label="4_group_1">
            <attvalue for="0" value="1"/>
        </node>    
        <node id="5" label="5_group_2">
            <attvalue for="0" value="2"/>
        </node>    
        <node id="6" label="6_group_2">
            <attvalue for="0" value="2"/>
        </node>    
        <node id="7" label="7_group_2">
            <attvalue for="0" value="2"/>
        </node>    
        <node id="8" label="8_group_2">
            <attvalue for="0" value="2"/>
        </node>    
              
    </nodes>

    <edges>
        <!-- Edges within groups -->
        <edge id="0" source="1" target="2" weight="0.25"/>
        <edge id="1" source="0" target="2" weight="0.88"/>
        
        <edge id="2" source="3" target="4" weight="1.00"/>
        
        <edge id="3" source="5" target="7" weight="0.52"/>    
        <edge id="4" source="7" target="8" weight="0.52"/>
        <edge id="5" source="6" target="8" weight="0.52"/>
        
        <!-- Edges across groups -->
        <edge id="6" source="0" target="3" weight="1.00"/>
        <edge id="7" source="2" target="4" weight="1.00"/>

        <edge id="8" source="1" target="7" weight="1.00"/> 
        <edge id="9" source="4" target="6" weight="1.00"/>
        <edge id="10" source="4" target="8" weight="1.00"/>

    </edges>

</graph>
</gexf>
    """
        fo = open(filename, 'w')
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

    def test_load_graph_gexf_three_adjacency_matrix(self):
        #                    0     1     2     3     4     5     6     7     8   
        result = np.matrix([[0.00, 0.00, 0.88, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00], # 0
                            [0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00], # 1 
                            [0.88, 0.25, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00], # 2
                            [1.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00], # 3
                            [0.00, 0.00, 1.00, 1.00, 0.00, 0.00, 1.00, 0.00, 1.00], # 4
                            [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.52, 0.00], # 5
                            [0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.52], # 6
                            [0.00, 1.00, 0.00, 0.00, 0.00, 0.52, 0.00, 0.00, 0.52], # 7
                            [0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.52, 0.52, 0.00]]) # 8

        graph = graphio.load_graph(self.test_three_group_gexf_file, format='GEXF')
        nodes = graph.nodes()
        adj_matrix = nx.adjacency_matrix(graph).todense()
        
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                result_i = nodes.index(str(i))  # Order of the nodes is not fixed
                result_j = nodes.index(str(j))
                self.assertEquals(adj_matrix[i,j], result[result_i,result_j])

    def test_node_attributes(self):
        graph = graphio.load_graph(self.test_file, format='GEXF')
        self.assertEquals(graph.node['0']['group'], '0')
        self.assertEquals(graph.node['1']['group'], '0')
        self.assertEquals(graph.node['2']['group'], '1')
        self.assertEquals(graph.node['3']['group'], '1')

    def test_file_with_no_group_attribute_raises_exception(self):
        with self.assertRaises(ValueError):
            graph = graphio.load_graph(self.test_no_attr_file)

    def test_file_with_missing_group_attributes_raises_exception(self):
        with self.assertRaises(ValueError):
            graph = graphio.load_graph(self.test_missing_attr_file)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraphIOFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # unittest.main()