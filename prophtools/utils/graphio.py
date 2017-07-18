#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
.. module:: graphio.py
.. moduleauthor:: Carmen Navarro Luzon

Functions for reading graph files.
"""

import networkx as nx
from prophtools.common.graphdata import GraphDataSet

def load_graph(filename, format="TGF"):
    fi = open(filename)

