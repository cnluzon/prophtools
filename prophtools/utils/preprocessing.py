#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
.. module:: preprocessing.py
.. moduleauthor:: Carmen Navarro Luzon

Functions for matrix preprocessing before prioritization.
Ported from Victor Martínez Octave version.
"""

import scipy.sparse as sparse


def LG(F, alpha, C_H, maxiter):
    initial_F = F
    for iter in range(maxiter):
        old_F = F
        F = alpha * C_H * old_F + (1-alpha) * initial_F
        if not ((max(max(abs(F - old_F)))) > 1e-9):
            break

    return [initial_F, F]


def precompute_matrix(m):
    """
    Returns the precomputed matrix for a normalized adjacency matrix m.
    m Must be normalized.

    Returns a sparse matrix (TODO: Change to keep sparsity)

    Arguments:
        m:      sparse matrix (normalized)
    """

    output = sparse.lil_matrix((m.shape))
    query = sparse.lil_matrix((m.shape[0], 1))

    for i in range(m.shape[0]):
        query[i] = 1
        [temp, precomp_score] = LG(query, 0.9, m, 1000)
        output[:, i] = precomp_score
        query[i] = 0

    return output


def normalize_matrix(m):
    """
    Returns the normalized matrix for an adjacency matrix m.

    Keeps the type of matrix (dense or sparse)
    Arguments:
        m:      csr_sparse matrix to normalize (sparse)
        
    """
    diagonal1 = sparse.lil_matrix((m.shape[0], m.shape[0]))
    diagonal2 = sparse.lil_matrix((m.shape[1], m.shape[1]))

    for i in range(m.shape[0]):
        value = m[i, :].sum()
        if value > 0:
            diagonal1[i, i] = value**(-0.5)
        else:
            diagonal1[i, i] = 0

    for i in range(m.shape[1]):
        value = m[:, i].sum()
        if value > 0:
            diagonal2[i, i] = value**(-0.5)
        else:
            diagonal2[i, i] = 0

    diagonal1 = sparse.lil_matrix(diagonal1)
    diagonal2 = sparse.lil_matrix(diagonal2)
    output = diagonal1 * m * diagonal2

    return output
