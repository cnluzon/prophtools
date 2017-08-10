#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
.. module:: graphio.py
.. moduleauthor:: Carmen Navarro Luzon

Functions for reading graph files.
"""

import networkx as nx
from prophtools.common.graphdata import GraphDataSet
import simplegexf
import shutil
import tempfile
import os

def _write_sample_gexf_file(filename):
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

def validate_allowed_format(f):
    allowed_formats = ['GEXF']
    if f.upper() not in allowed_formats:
        return False
    return True

def load_graph(filename, format="GEXF"):
    format_ok = validate_allowed_format(format)
    if not format_ok:
        msg = "Unknown format: {}".format(format)
        raise TypeError(msg)
    
    graph = nx.read_gexf(filename)
    load_node_attributes(graph, filename)
    return graph

def load_node_attributes(graph, filename):
    """
    Loads node attributes to a graph already loaded using networkx. The reason
    for this is that currently networkx does NOT implement node attribute parsing.
    """
    gexf = simplegexf.Gexf(filename)
    # print dir(gexf)
    
    attributes_list = gexf.data['graph']['attributes']['attribute']
    group_attribute_id = None

    att_names = []
    try:    
        att_names = [a['@title'] for a in attributes_list]
    except TypeError:
        att_names = [attributes_list['@title']]

    if 'group' not in att_names:
        msg = "Invalid node attributes. These should include a group integer attribute"
        raise ValueError(msg)

    if not isinstance(attributes_list, list):
        attributes_list = [attributes_list]

    for a in attributes_list:
        if a['@title'] == 'group':
            group_attribute_id = a['@id']
            if a['@type'] != 'integer':
                msg = "Invalid troup type attribute. Should be an integer."
                raise ValueError(msg)


    nodes_list = gexf.data['graph']['nodes']['node']

    node_attributes = {}
    for n in nodes_list:
        node_id = n['@id']
        group_value = find_tag_value(n['attvalue'], group_attribute_id)
        if not group_value:
            msg = "Found a node with no group attribute {}".format(node_id)
            raise ValueError(msg)

        node_attributes[node_id] = group_value

    nx.set_node_attributes(graph, 'group', node_attributes)
    return graph


def find_tag_value(att_list, att_id):
    if not isinstance(att_list, list):
        att_list = [att_list]

    for attribute in att_list:
        if attribute['@for'] == att_id:
           return attribute['@value']

    return None

def convert_to_mat(graph):
    pass

if __name__ == "__main__":
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, 'temp.gexf')
    _write_sample_gexf_file(test_file)

    g = load_graph(test_file)
    shutil.rmtree(test_dir)