====================================================================================
ProphTools. General Prioritization Tools for Heterogeneous Biological Networks
====================================================================================

Authors: Carmen Navarro Luzón, Víctor Martínez Gómez

.. image:: https://coveralls.io/repos/github/cnluzon/prophtools/badge.svg
    :target: https://coveralls.io/github/cnluzon/prophtools

.. image:: https://travis-ci.org/cnluzon/prophtools.svg?branch=master
    :target: https://travis-ci.org/cnluzon/prophtools  
   
About ProphTools
================

``ProphTools`` package allows to perform heterogeneous network prioritization on a set 
of interconnected networks, prioritizing from a query network to the target 
network by means of a hybrid approach including a Random Walk with Restarts for
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


Martínez, Víctor, Cano, Carlos, and Blanco, Armando.
**ProphNet: A generic prioritization method through propagation of information.**
BMC bioinformatics 15.1 (2014): 1.


License
=======
``ProphTools`` is implemented in python and source code is provided under the 
GPLv3.0 license. You can see more about its terms on the LICENSE.txt file.


Installation
============

``ProphTools`` is provided as a python 2.7 package. At the moment it is not 
available on PyPi, but you can download the `tar ball source distribution file <https://github.com/cnluzon/prophtools/raw/master/dist/prophtools-1.0.tar.gz>`_
and install it: ::

    pip install ./prophtools-1.0.tar.gz

If the above link does not work, you can find the tar.gz file under /dist/ at the prophtools repository.

Requirements
============

``ProphTools`` Requires python ``2.7`` to work, along with the following libraries (tested for the specified versions): ::

    numpy (>=1.11.2)
    scipy (>=0.18.1)
    matplotlib (>=1.4.3)
    scikit-learn (>=0.18)
    networkx (>=1.11) 

All requirements are included in the ``setup.py``. However, scipy documentation suggests installing it through ``apt-get``: <http://www.scipy.org/install.html>. If you run into problems with pip I recommend to previously install scipy, numpy and matplotlib through apt-get to ensure it will work: ::

    sudo apt-get install python-numpy python-scipy python-matplotlib
    
Docker version
==============
If you prefer to forget about requirements or are running another operating system, you can use prophtools public docker version to run it as a docker container. Prophtools docker container is available at the ``Docker hub``: <https://hub.docker.com/r/cnluzon/prophtools/>. You can pull it by: ::

    docker pull cnluzon/prophtools
    
For more information about how to install and use Docker, you can read the 
`Docker documentation <https://docs.docker.com/>`_.

Example runs on an installed docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once you have pulled the prophtools Docker image, you can run it using `docker run` command. Keep in mind that prophtools requires input files. In this sense, you need to mount a docker data volume to use it. This can be done using the `-v` option. For instance, if you are running prophtools on a directory which has a sampledata/ directory in it which contained an example.mat: ::

    docker run -v `pwd`/sampledata:/sampledata cnluzon/prophtools cross --matfile /sampledata/example.mat --src 0 --dst 1 --out /sampledata/prueba

Note that you need to provide the full path to the directory that is going to be mounted by the docker container. Additionally, note that the output files persist in the data volume. 

How to use
==========

``Prophtools`` is a command line tool. It runs internally on .mat files (for more information, see **Network configuration file format** below). In order to improve usability, the latest version of ProphTools includes conversion to this .mat formal from two file formats: 

* **TXT format** based on Trivial Graph Format (TGF).
* **Graph Exchange XML format (GEXF)**. XML-based Graph specification used in many applications: https://gephi.org/gexf/format/.

ProphTools input file description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned above, ``ProphTools`` can convert two types of graph specification files to its internal ``.mat`` files. This can be done by the following command: ::

    prophtools buildmat --file toy_example.txt --format txt --out toy_example.mat

Where format can be either txt or gexf, the current supported file formats. This process will also build the **precomputed** matrices that ProphTools requires to improve computation time. Please note that precomputing can take long time in large matrices. However, this process only needs to take place once.

TXT file format
---------------
The simplest file format ProphTools can handle is a TXT file based on Trivial Graph Format (TGF). Trivial Graph Format only includes a list of nodes and a list of edges, as in: ::

    1 FirstNode
    2 SecondNode
    #
    1 2 Edge

To this format, a third column to the node list has been added to provide subnetwork information. Additionally, edges must provide a weight value: ::

    1 FirstNode node_group
    2 SecondNode node_group
    #
    1 2 Edge edge_weight

A toy example with three subnetworks: ::

    0 node_0 0
    1 node_1 0
    2 node_2 0
    3 node_3 1
    4 node_4 1
    5 node_5 2
    6 node_6 2
    7 node_7 2
    8 node_8 2
    ##
    1 2 0.25
    0 2 0.88
    3 4 1.00
    5 7 0.52
    7 8 0.52
    6 8 0.52
    0 3 1.00
    2 4 1.00
    1 7 1.00
    4 6 1.00 
    4 8 1.00

Please note that node ids must be unique, even if they belong to different subnetworks. By default, ProphTools will use node identifiers, not labels (second column in txt file) as IDs for nodes. Optionally, you can use the ``--labels_as_ids`` parameter to use labels instead. Please note that in this case labels must be unique per node.

GEXF file format
----------------

GEXF (https://gephi.org/gexf/format/) is an adaptation of XML used to specify graphs. As you can see in prophtools/matfiles/toy_example.gexf, ProphTools supported GEXF file needs that you include a 'group' label for each node, specifying which subnetwork each node belongs to, for instance, this would be a trivial GEXF file with only one subnetwork with two nodes: ::

    <?xml version="1.0" encoding="UTF-8"?>
    <gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <meta lastmodifieddate="2017-09-04">
    <creator>cnluzon</creator>
    <description>Toy example gexf file to understand use with ProphTools</description>
    </meta>
    <graph defaultedgetype="undirected" mode="static">
        <!-- Required: group attribute for each node -->
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
        </nodes>

        <edges>
            <edge id="0" source="0" target="1" weight="0.25"/>
        </edges>
    
    </graph>
    </gexf>

If you want to know more, see the two examples on the matfiles folder that comes with `ProphTools`.

`ProphTools` will take as an input a .mat file containing your network configuration. In order to obtain this file, it is necessary that you run `ProphTools buildmat` as explained before. Once you have your `.mat` file, you can perform two types of tasks.


Prioritize on a network configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`ProphTools` will take the aforementioned `mat` file and and three more required parameters: 

* ``src``: source network, 
* ``dst``: destination network, and
* ``qindex`` or ``qname``: a list of indexes or ids separated by commas containing the source network
node indexes that are going to be propagated.

Note that ``src`` and ``dst`` correspond to the group index provided in the txt or gexf files.

For instance: ::

    prophtools prioritize --matfile example.mat --src 0 --dst 2 --qindex 1,2

will return a scored list of nodes from the destination network and their
correlation scores: ::

    Entity	Score
    c_00003	0.105975
    c_00017	0.104684
    c_00015	0.070770
    c_00012	0.040780
    c_00002	0.031075

    
Or: ::

    prophtools prioritize --matfile example.mat --src 0 --dst 2 --qname a_00001,a_00002

will output the same result. Optionally, a ``out`` parameter can be provided to save all results as a comma-separated value ``csv`` file format.

Correlation score is a value between -1.0 and 1.0, as it correspond to Pearson
correlation (or Spearman if specified.)

Optionally, a ``--corr_function`` parameter can be provided to specify spearman
correlation: ::

    prophtools prioritize --matfile network.mat --src 0 --dst 2 --qindex 1,2 --corr_function spearman

Performance test on a network set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given an input .mat file, `ProphTools` can also give you an estimation on how
well the propagation method predicts a certain connection by performing a 
leave-one-out cross-validation on the relation you choose.

The required parameters in this case are:

* ``matfile``: Input ``mat`` network configuration file.
* ``src``: Origin network (as specified by the ``group`` label in either ``GEXF`` or ``TXT`` file).
* ``dst``: Destination network (as specified by the ``group`` label in either ``GEXF`` or ``TXT`` file).

Optionally, you can specify:

* ``cross```: Number of groups for the cross validation. 5 by default.
* ``corr_function``: Correlation function used to compute final scores. By default, this is Pearson correlation. Optionally, you can specify spearman.

For instance, to run ``ProphTools`` cross validation on the example data using spearman correlation function: ::

    prophtools cross --matfile example.mat --src 0 --dst 2 --cross 5 --out results --corr_function spearman

This will save some info in ``results.txt`` regarding AUC and Average ranking values per prioritization process, and also a results.svg ROC curve will be plotted. Note that this process is more time consuming than mere prioritization, because it runs a prioritization with every node on the source network.

Using the defaults: ::

    prophtools cross --matfile example.mat --src 0 --dst 2


**APPENDIX: ProphTools native Network configuration file format**

As of ``ProphTools`` v1.1, you are no longer required to build this data on your own. However,
this description is kept for users that prefer this format to the text-based formats described before.

The ``--matfile`` parameter is required for all prophtools function. It is a .mat 
file that can be generated from scipy sparse matrices using the scipy.io
module and its ``loadmat`` and ``savemat`` functions.

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
    
    
LncRNA-disease network
^^^^^^^^^^^^^^^^^^^^^^

Additionally, you can download real lncRNA-disease data from our server: `general dataset <http://genome.ugr.es:9000/download/data/lncrna_disease_prophtools_general.mat>`_, `specific dataset <http://genome.ugr.es:9000/download/data/lncrna_disease_prophtools_specific.mat>`_.

Drug-gene-disease network
^^^^^^^^^^^^^^^^^^^^^^^^^

You can also download 
data from our server: `DrugNet file (large, includes precomputed matrices) <http://genome.ugr.es:9000/download/data/drugnet_data.zip>`_. `DrugNet file (lighter, but needs precomputation before use) <http://genome.ugr.es:9000/download/data/drugnet_data_non_precomputed.zip>`_. For more information, you can visit `DrugNet's website <http://genome.ugr.es:9000/drugnet>`_.

If you use these datasets, please cite us:

Martínez, V., Navarro, C., Cano, C., Fajardo, W., Blanco, A. 
**DrugNet: Network-based drug–disease prioritization by integrating heterogeneous data.** 
Artificial intelligence in medicine, 63(1), 41-49. (2015).




