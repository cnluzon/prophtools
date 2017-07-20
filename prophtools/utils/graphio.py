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
    self.load_node_attributes(graph, filename)
    return graph

def load_node_attributes(graph, filename):
    """
    Loads node attributes to a graph already loaded using networkx. The reason
    for this is that currently networkx does NOT implement node attribute parsing.
    """
    gexf = simplegexf.Gexf(filename)
    
