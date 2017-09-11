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


def validate_allowed_format(f):
    allowed_formats = ['GEXF', 'TXT']
    if f.upper() not in allowed_formats:
        return False
    return True

def load_graph(filename, format="GEXF"):
    format_ok = validate_allowed_format(format)
    if not format_ok:
        msg = "Unknown format: {}".format(format)
        raise TypeError(msg)
    
    if format.lower() == "gexf":
        graph = nx.read_gexf(filename)
        load_node_attributes(graph, filename)

    elif format.lower() == "txt":
        graph = read_txt_graph(filename)

    return graph

def read_txt_graph(filename):
    fi = open(filename)
    node_list = read_txt_nodes(fi)
    edge_list = read_txt_edges(fi)

    result_graph = nx.Graph()
    result_graph.add_nodes_from(node_list)
    result_graph.add_edges_from(edge_list)


    fi.close()
    return result_graph

def read_txt_nodes(fi):
    result = []
    line = fi.readline()
    node_id_list = []
    group_list = set()

    while line and line[0:2] != "##":
        fields = line.rstrip().split()
        group = ''
        if len(fields) == 2:
            if group_list:
                msg = "Wrong file format. Missing group for node {}.".format(node_id)
                raise ValueError(msg)
            else:
                msg = "WARNING: Missing group field. Assuming homogeneous network."
                group = '0'

        elif len(fields) < 2:
            msg = "Wrong file format. Missing fields in line {}".format(str(fields))
            raise ValueError(msg)

        else:
            group = fields[2]
            group_list.add(group)

        node_id = fields[0]
        node_info = (node_id, {'label':fields[1], 'group':group})
        if node_id in node_id_list:
            msg = "Node IDs must be unique. Found repeated element {}".format(node_id)
            raise ValueError(msg)

        node_id_list.append(node_id)

        result.append(node_info)
        line = fi.readline()

    if not line:
        print "Warning: Empty line reached with no ## edge signal found."
    return result 

def read_txt_edges(fi):
    result  =[]
    line = fi.readline()
    while line:
        fields = line.rstrip().split()
        try:
            edge_info = (fields[0], fields[1], {'weight': float(fields[2])})
        except ValueError:
            msg = "Edge info fields must be src (ID), dst (ID) and weight in that order. Weight must be a floating point number."
            raise ValueError(msg)

        result.append(edge_info)
        line = fi.readline()

    return result

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
    node_names = {}
    for n in nodes_list:
        node_id = n['@id']
        node_name = n.get('@label', '')

        group_value = "0"
        if group_attribute_id:
            group_value = find_tag_value(n['attvalue'], group_attribute_id)

            if not group_value:
                msg = "Found a node with no group attribute: {}".format(node_id)
                raise ValueError(msg)

        node_attributes[node_id] = group_value
        node_names[node_id] = node_name

    nx.set_node_attributes(graph, 'group', node_attributes)
    nx.set_node_attributes(graph, 'label', node_names)

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
        node_label = graph.node[n].get('label', '')
        try:
            groups[group_tag].append((n, node_label))
        except KeyError:
            groups[group_tag] = [(n, node_label)]

    return groups

def build_within_group_matrix(graph, group_node_list, group_tag, precompute=False, labels_as_ids=False):
    result_mat = []
    adj_mat = nx.adjacency_matrix(graph).todense()

    global_node_list = graph.nodes()
    if labels_as_ids:
        global_node_list = [graph.node[n]['label'] for n in global_node_list]

    indices = [global_node_list.index(n) for n in group_node_list]

    result_mat = adj_mat[indices,:]
    result_mat = result_mat[:, indices]

    if precompute:
        entity = EntityNet.from_raw_matrix(scipy.sparse.csr_matrix(result_mat), group_tag, group_node_list)
    else:
        entity = EntityNet(scipy.sparse.csr_matrix(result_mat), group_tag, group_node_list)

    return entity 

def build_across_groups_matrix(graph, src_node_list, dst_node_list, relation_tag, labels_as_ids=False):
    result_mat = []
    adj_mat = nx.adjacency_matrix(graph).todense()
    global_node_list = graph.nodes()
    if labels_as_ids:
        global_node_list = [graph.node[n]['label'] for n in global_node_list]

    src_indices = [global_node_list.index(n) for n in src_node_list]
    dst_indices = [global_node_list.index(n) for n in dst_node_list]

    result_mat = adj_mat[src_indices,:]
    result_mat = result_mat[:,dst_indices]

    if np.count_nonzero(result_mat) > 0:
        return RelationNet(scipy.sparse.csr_matrix(result_mat), relation_tag)
    else:
        return None

def convert_to_graphdataset(graph, precompute=False, labels_as_ids=False):
    converted_object = None

    networks = []
    relations = []

    adj_matrix = nx.adjacency_matrix(graph).todense()
    node_list = graph.nodes()

    groups = separate_node_tags_per_group(graph)
    groups_list = sorted(groups.keys())

    if len(groups_list) > 10:
        msg = "WARNING: Number of groups higher than 10."
        msg += " Please, check that group tag in the input file corresponds to the different types of entities, not to node ID"
        raise ValueError(msg)

    for g in groups_list:
        id_list = []
        if labels_as_ids:
            id_list = [v[1] for v in groups[g]]
            if len(id_list) > len(set(id_list)):
                msg = """Repeated labels on the id_list for {}. If you use labels_as_ids,
                all labels provided must be unique. Id list obtained: {}""".format(
                    g, str(id_list))
                raise ValueError(msg)

        else:
            id_list = [v[0] for v in groups[g]]

        m = build_within_group_matrix(graph, id_list, g, precompute=precompute, labels_as_ids=labels_as_ids)
        networks.append(m)

    # super-adjacency matrix is a |groups|x|groups| matrix
    connections_mat = np.zeros((len(groups), len(groups)), dtype=int)
    connections_mat.fill(-1)

    for i in range(len(groups_list)):
        for j in range(i+1, len(groups_list)):
            src_tag = groups_list[i]
            dst_tag = groups_list[j]
            relation_tag = "{}_{}".format(src_tag, dst_tag)
            src_id_list = []
            dst_id_list = []
            if labels_as_ids:
                src_id_list = [v[1] for v in groups[src_tag]]
                dst_id_list = [v[1] for v in groups[dst_tag]]
            else:
                src_id_list = [v[0] for v in groups[src_tag]]
                dst_id_list = [v[0] for v in groups[dst_tag]]

            m = build_across_groups_matrix(graph, src_id_list, dst_id_list, relation_tag, labels_as_ids=labels_as_ids)
            if m:
                relations.append(m)
                connections_mat[i,j] = len(relations)-1

    converted_object = GraphDataSet(networks, relations, connections_mat)
    return converted_object
