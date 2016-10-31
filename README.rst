================================================================
ProphTools v1.0. Tools for Heterogeneous Network prioritization
================================================================

Authors: Carmen Navarro Luzón, Víctor Martínez Gómez

About ProphTools
================

``ProphTools`` allow to perform heterogeneous network prioritization on a set 
of interconnected networks, prioritizing from a query network to the target 
network by means of a hybrid approach including a Random Walk with Restarts
within network approach and propagation across different networks based on these
results. Final scores are computed correlating the results from
propagating from the query network to the target network and correlating target
nodes from within the target network. ``ProphTools`` is based on the core 
methodology applied to create ``ProphNet``, a web-based prioritization tool that performs
queries on a specific gene-domain-disease network.

ProphTools methodology allows to handle any type of network
configuration, so you can now download the ``ProphTools`` package,
set up your network configuration and run queries and performance tests.

In addition, as the source code is provided, you are free to use ``ProphTools``
as an API and pass your network configuration as a ``GraphDataSet`` object to a 
ProphNet prioritizer. 

For more specific information about the propagation algorithms, please read our 
`publication <http://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-15-S1-S5>`_:

Martínez, Víctor, Carlos Cano, and Armando Blanco. 
**ProphNet: A generic prioritization method through propagation of information.**
BMC bioinformatics 15.1 (2014): 1.


License
=======
``ProphTools`` is implemented in python and source code is provided under the 
GPLv3.0 license. You can see more about its terms on the LICENSE.txt file.


Installation
============

``ProphTools`` is provided as a python 2.7 package. At the moment it is not 
available on PyPi, but you can download the tar ball source distribution file 
and install it: ::

    pip install ./prophtools-1.0.tar.gz

How to use
==========

Prophtools is a command line tool. Right now, it has two main functionalities:

Prioritize on a network set
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prophtools will take as an input a .mat file containing your network configuration
and three more required parameters: 

source network (src), 
destination network (dst), and
query list (a list of indexes separated by commas containing the source network
node indexes that are going to be propagated).

For instance: ::

    prophtools prioritize --matfile network.mat --src 0 --dst 2 --query 1,2

will return a scored list of nodes from the destination network and their
correlation scores: ::

    Entity  Score
    c_00017   0.1016
    c_00003   0.0902
    c_00012   0.0581
    c_00013   0.0545
    c_00019   0.0461

Correlation score is a value between -1.0 and 1.0, as it correspond to pearson
correlation (or spearman if specified.)

Optionally, a --corr_function parameter can be provided to specify spearman
correlation: ::

    prophtools prioritize --matfile network.mat --src 0 --dst 2 --query 1,2 --corr_function spearman

**Network configuration file format**

The ``--matfile`` parameter is required for all prophtools function. It is a .mat 
file that can be generated from scipy sparse matrices using the scipy.io
module and its ``loadmat`` and ``savemat`` functions.

The generality of ``ProphTools``prioritization requires you to provide some meta-data along with the
adjacency matrices for the entities and the relations involved in your network configuration.

``scipy.io`` returns a dictionary where the keys are the names of the entities contained
on the .mat file. In the case of ``ProphTools``, the meta-data must be: ::

    'entities':    A list of names corresponding to the name of the entity networks.
    'relations':   A list of names corresponding to the name of the relation networks.
    'connections': A square matrix of shape len(entities)xlen(entities) where
                   connections[i,j]==2 means relations[2] connects entities[i] and
                   entities[j], in a way that the ROWS in relations[2] represent
                   entities[i] and the COLUMNS represent entities[j]. For this 
                   reason, connections is a non-symmetric matrix, meaning 
                   connections[j,i]==-1.

For each name in ``entities``, there must be an entry with that name pointing to
a matrix, and also the same for ``relations``. In addition, for each of the names
there will be a list of node names (to label the queries) and a precomputed matrix.

**Example:**
As an example, imagine that we have the following network set: three entity networks,
A, B and C, where A is connected to B with the relation REL_AB, and B is connected
to C with the relation matrix REL_BC. We would have this configuration. The required
meta-data would be: ::

     'entities':    ['A', 'B', 'C']
     'relations':   ['REL_AB', 'REL_BC']
     'connections': [[-1,  0, -1],   # connections[0,1]==0 means relations[0] connects entities[0] and entities[1]
                     [-1, -1,  1],
                     [-1, -1, -1]]

Then, the actual adjacency matrices are provided: ::

    'A': a square matrix
    'A_precomputed': a square matrix same shape of A
    'A_name': list of names for the nodes of A (its length is the same as A.shape)
    'B': a square matrix
    'B_precomputed': a square matrix same shape of B
    'B_name': list of names for the nodes of B (its length is the same as B.shape)
    'C': a square matrix
    'C_precomputed': a square matrix same shape of C
    'C_name': list of names for the nodes of C (its length is the same as C.shape)

    'REL_AB': a matrix where rows correspond to A, columns to B, therefore its shape: rowsA x columnsB.
    'REL_BC': a matrix where rows correspond to B, columns to C, therefore its shape: rowsB x columnsC.

Please note that if a matrix is named X, the precomputed matrix must be X_precomputed, and
the name list X_name, since ``GraphDataSet`` IO parses the .mat file this way. Also note that
precomputed matrices **must** be provided at this moment. To precompute them you can make use
of the ``preprocessing`` module provided.

There is a sample example.mat matrix file that you can download under ``matfiles/example.mat`` to familiarize yourself
with the format. 

On python command line: ::

    %> import scipy.io as sio
    %> sio.whosmat('example.mat')

    [('a', (50, 50), 'sparse'),
     ('c', (20, 20), 'sparse'),
     ('b', (25, 25), 'sparse'),
     ('b_precomputed', (25, 25), 'sparse'),
     ('c_name', (20,), 'char'),
     ('rel_bc', (25, 20), 'sparse'),
     ('rel_ab', (50, 25), 'sparse'),
     ('rel_ac', (50, 20), 'sparse'),
     ('c_precomputed', (20, 20), 'sparse'),
     ('relations', (3,), 'char'),
     ('connections', (3, 3), 'int64'),
     ('entities', (3,), 'char'),
     ('a_name', (50,), 'char'),
     ('b_name', (25,), 'char'),
     ('a_precomputed', (50, 50), 'sparse')]

    %> my_data = sio.loadmat('example.mat')
    %> a['a']
    <50x50 sparse matrix of type '<type 'numpy.float64'>'
        with 1730 stored elements in Compressed Sparse Column format>
    

Performance test on a network set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Given an input .mat file, prophtools can also give you an estimation on how
well the propagation method predicts a certain connection by performing a 
leave-one-out cross-validation on the relation you choose.

The required parameters in this case are:

* matfile: Input network configuration file
* src: Origin network
* dst: Destination network

Optionally, you can specify
* cross: Number of groups for the cross validation. By default, this is 5.
* corr_function: Correlation function used to compute final scores. By default, this is pearson correlation. Optionally, you can specify spearman.
