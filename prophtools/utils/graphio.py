#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
.. module:: graphio.py
.. moduleauthor:: Carmen Navarro Luzon

Functions for reading graph files.
"""

import networkx as nx
import numpy as np
from prophtools.common.graphdata import GraphDataSet, RelationNet, EntityNet
import scipy.sparse
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
    nodes_list = gexf.data['graph']['nodes']['node']

    att_names = []
    try:    
        att_names = [a['@title'] for a in attributes_list]
    except TypeError:
        att_names = [attributes_list['@title']]

    if 'group' not in att_names:
        msg = "Warning: No group attribute found. A single network will be considered."
        # raise ValueError(msg)
        print msg

    group_attribute_id = find_tag_attribute(attributes_list, 'group')

    node_attributes = {}
    for n in nodes_list:
        node_id = n['@id']
        node_name = n['@label']
        group_value = "0"
        if group_attribute_id:
            group_value = find_tag_value(n['attvalue'], group_attribute_id)

            if not group_value:
                msg = "Found a node with no group attribute: {}".format(node_id)
                raise ValueError(msg)

        node_attributes[node_id] = group_value

    nx.set_node_attributes(graph, 'group', node_attributes)

    return graph

def find_tag_attribute(att_list, att_id):
    if not isinstance(att_list, list):
        att_list = [att_list]

    group_attribute_id = None
    for a in att_list:
        if a['@title'] == att_id:
            group_attribute_id = a['@id']

    return group_attribute_id

def find_tag_value(att_list, att_id):
    if not isinstance(att_list, list):
        att_list = [att_list]

    for attribute in att_list:
        if attribute['@for'] == att_id:
           return attribute['@value']

    return None

def separate_node_tags_per_group(graph):
    groups = {}
    node_list = graph.nodes()
    for n in node_list:
        group_tag = graph.node[n]['group']
        try:
            groups[group_tag].append(n)
        except KeyError:
            groups[group_tag] = [n]

    return groups

def build_within_group_matrix(graph, group_node_list, group_tag, precompute=False):
    result_mat = []
    adj_mat = nx.adjacency_matrix(graph).todense()
    global_node_list = graph.nodes()

    indices = [global_node_list.index(n) for n in group_node_list]

    result_mat = adj_mat[indices,:]
    result_mat = result_mat[:, indices]

    if precompute:
        entity = EntityNet.from_raw_matrix(scipy.sparse.csr_matrix(result_mat), group_tag, group_node_list)
    else:
        entity = EntityNet(scipy.sparse.csr_matrix(result_mat), group_tag, group_node_list)

    return entity 

def build_across_groups_matrix(graph, src_node_list, dst_node_list, relation_tag):
    result_mat = []
    adj_mat = nx.adjacency_matrix(graph).todense()
    global_node_list = graph.nodes()

    src_indices = [global_node_list.index(n) for n in src_node_list]
    dst_indices = [global_node_list.index(n) for n in dst_node_list]

    result_mat = adj_mat[src_indices,:]
    result_mat = result_mat[:,dst_indices]

    if np.count_nonzero(result_mat) > 0:
        return RelationNet(scipy.sparse.csr_matrix(result_mat), relation_tag)
    else:
        return None

def convert_to_graphdataset(graph, precompute=False):
    converted_object = None

    networks = []
    relations = []

    adj_matrix = nx.adjacency_matrix(graph).todense()
    node_list = graph.nodes()

    groups = separate_node_tags_per_group(graph)
    groups_list = sorted(groups.keys())

    if len(groups_list) > 10:
        msg = "WARNING: Number of groups higher than 10."
        msg += " Please, check that group tag in the XML file corresponds to the different types of entities, not to node ID"
        raise ValueError(msg)

    for g in groups_list:
        m = build_within_group_matrix(graph, groups[g], g, precompute=precompute)
        networks.append(m)

    # super-adjacency matrix is a |groups|x|groups| matrix
    connections_mat = np.zeros((len(groups), len(groups)), dtype=int)
    connections_mat.fill(-1)

    for i in range(len(groups_list)):
        for j in range(i+1, len(groups_list)):
            src_tag = groups_list[i]
            dst_tag = groups_list[j]
            relation_tag = "{}_{}".format(src_tag, dst_tag)
            m = build_across_groups_matrix(graph, groups[src_tag], groups[dst_tag], relation_tag)
            if m:
                relations.append(m)
                connections_mat[i,j] = len(relations)-1

    converted_object = GraphDataSet(networks, relations, connections_mat)
    return converted_object

if __name__ == "__main__":
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, 'temp.gexf')
    _write_sample_gexf_file(test_file)

    g = load_graph(test_file)
    shutil.rmtree(test_dir)