# -*- coding: latin-1 -*-

"""
Prophtools: Tools for heterogenoeus network prioritization.

Copyright (C) 2016 C. Navarro Luzón, V. Martínez Gómez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

.. module :: metrics.py
.. moduleauthor :: C. Navarro Luzón, V. Martínez Gómez

Perform tests on prioritizations to check the quality of the network
configuration.

"""

import matplotlib.pyplot as plt
import random
import scipy.sparse as sparse
from scipy import interp
import numpy as np

from sklearn.model_selection import KFold
import sklearn.metrics as skmetrics


class PrioritizationTest:
    def __init__(self, prioritizer):
        self.prioritizer = prioritizer
        random.seed(3)

    def compute_rank(self, scores, index):
        index_score = scores[index]
        sorted_scores = sorted(scores, reverse=True)
        return sorted_scores.index(index_score)

    def remove_test_edges(self, matrix, test_edges):
        old_values = np.zeros(len(test_edges))
        for i, edge in enumerate(test_edges):
            old_values[i] = matrix[edge[0], edge[1]]
            matrix[edge[0], edge[1]] = 0

        return old_values

    def remove_all_edges(self, matrix, test_edges):
        """
        Remove all edges connecting entities connected by edges in the
        test_edges list. This means, if e in test_edges connects A and B,
        remove all edges coming from A and to B from the dataset.
        """
        for edge in test_edges:
            matrix[edge[0], :] = 0
            matrix[:, edge[1]] = 0

    def restore_test_edges(self, matrix, test_edges, values):
        for i, edge in enumerate(test_edges):
            matrix[edge[0], edge[1]] = values[i]

    def run_cross_validation(self, origin, destination, fold=10, out='test.out',
                             corr_function="pearson", extreme=False):
        """
        Performs a LOO-CV experiments on the prioritizer, from origin matrix
        to destination matrix.

        Args:
            origin: Index of the origin matrix.
            destination: Index of the destination matrix.
            fold: Cross-Validation fold. If None, performs a leave one out
                  experiment.
            out: Filename to store auc values.
            corr_function:  How to correlate values in the last stage of
                prioritization propagation. By default,
                pearson correlation si computed, although also spearman
                correlation  is allowed.
        """

        if origin == destination:
            msg = ("Cannot run cross validation experiment on single matrix."
                   " Origin and destination must be different.")
            raise ValueError(msg)

        tested_relation = self.prioritizer.graphdata.get_connection(
            origin,
            destination).matrix

        relation_direction = self.prioritizer.graphdata.get_connection_direction(
            origin, destination)

        n_results = tested_relation.shape[1]

        [nonzero_rows, nonzero_cols] = tested_relation.nonzero()

        indexes = range(len(nonzero_rows))
        if fold is None:
            fold = len(indexes)

        kf = KFold(n_splits=fold)

        fold_auc = []
        mean_tpr = 0.0
        mean_fpr = np.linspace(0, 1, 100)
        ranks = []
        scores_per_test = []
        fold_number = 0
        test_number = 0

        for train, test in kf.split(indexes):
            test_edge_list = [(nonzero_rows[i], nonzero_cols[i]) for i in test]
            relation_copy_for_removal = sparse.lil_matrix(tested_relation)
            if extreme:
                self.remove_all_edges(relation_copy_for_removal, test_edge_list)
            else:
                old_values = self.remove_test_edges(relation_copy_for_removal,
                                                    test_edge_list)

            if relation_direction == 0:
                relation_copy_for_removal = relation_copy_for_removal.transpose()

            self.prioritizer.graphdata.set_relation_matrix(
                origin,
                destination,
                relation_copy_for_removal)

            for t in test:
                tagged_scores = self.prioritizer.propagate([nonzero_rows[t]],
                                                    origin,
                                                    destination,
                                                    corr_function=corr_function)

                scores = [s[0] for s in tagged_scores]

                if scores is not None:
                    test_rank = self.compute_rank(scores, nonzero_cols[t])

                    ranks.append(test_rank)
                    scores_per_test.append(scores[nonzero_cols[t]])

                    labels = np.zeros(len(scores), dtype=np.int)
                    labels[nonzero_cols[t]] = 1
                    fpr, tpr, thresholds = skmetrics.roc_curve(labels,
                                                               scores,
                                                               pos_label=1)

                    mean_tpr += interp(mean_fpr, fpr, tpr)
                    roc_auc = skmetrics.auc(fpr, tpr)
                    fold_auc.append(roc_auc)

                    test_number += 1
                else:
                    print "Warning, test resulting in empty scores."

            to_restore = tested_relation
            if relation_direction == 0:
                to_restore = tested_relation.transpose()

            self.prioritizer.graphdata.set_relation_matrix(origin, destination, to_restore)
            fold_number += 1

        # ranks normalize on size of the matrix,  whereas tpr/fpr on number of 
        # tests performed (i.e. edges connecting origin and destination)
        mean_tpr = mean_tpr/float(test_number)
        mean_tpr[-1] = 1.0
        mean_auc = skmetrics.auc(mean_fpr, mean_tpr)
        std_auc = np.std(fold_auc)

        mean_ranks = np.mean(ranks)
        std_ranks = np.std(ranks)
        mean_ranks_norm = mean_ranks/float(n_results)
        std_ranks_norm = std_ranks/float(n_results)

        self.write_metrics_to_file(mean_tpr, mean_fpr, mean_auc, std_auc,
                                   mean_ranks, std_ranks, mean_ranks_norm,
                                   std_ranks_norm, out=out)

        self.plot_roc(mean_fpr, mean_tpr, mean_auc, out)

    def write_metrics_to_file(self, mean_tpr, mean_fpr, mean_auc, std_auc,
                              mean_ranks, std_ranks, mean_ranks_norm,
                              std_ranks_norm, out='test'):

        fo = open('{}.txt'.format(out), 'w')
        fo.write("Avg. AUC       (std): {:10.4f}({:10.4f})\n".format(mean_auc, std_auc))
        fo.write("Avg. Rank      (std): {:10.4f}({:10.4f})\n".format(mean_ranks, std_ranks))
        fo.write("Avg. Rank Norm (std): {:10.4f}({:10.4f})\n".format(mean_ranks_norm, std_ranks_norm))
        fo.close()

        fo = open('{}_auc_data.txt'.format(out), 'w')
        fo.write("Avg tpr\tAvg fpr\n")
        for i in range(len(mean_fpr)):
            fo.write("{:10.4f}\t{:10.4f}\n".format(mean_tpr[i], mean_fpr[i]))

        fo.close()

    def plot_roc(self, fpr, tpr, roc_auc, out='test'):
        plt.figure()
        lw = 2
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC curve')
        plt.legend(loc="lower right")

        plt.savefig('{}.svg'.format(out))
