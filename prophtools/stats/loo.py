#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
 .. module :: loo.py
 .. moduleauthor :: C. Navarro Luzón, V. Martínez Gómez

Perform leave one out cross validation test on a network setup.

"""
import os

from prophtools.utils import validation
from prophtools.utils.experiment import Experiment

import prophtools.common.method as method
import prophtools.common.graphdata as graphdata
import prophtools.stats.metrics as metrics


class LOOExperiment(Experiment):
    """
    Experiment for running a LOO test on a certain network configuration.
    """

    def _print_help(self):
        help_message = """
ProphTools cross: Run a LOO-CV test on a network configuration.

Required parameters:
    matfile: mat file containing the networks and their configuration (see
             ProphTools documentation for more info on this format.)
    src    : Source network (as an index)
    dst    : Destination network (as an index)
    cross  : Number of groups ([2,20])
    mode   : How many edges are removed. normal: only test edge. extreme: all edges
             connecting involved nodes. semi: all edges connecting involved nodes only in propagation direction.
    out    : Name of the output files prefix (no extension). Three files will
             be generated: a .svg containing a ROC curve, a .txt containing the
             fpr/tpr values used to generate the plot and a .txt containing
             basic metrics (AUC and average ranks for the prioritized
             connections). By default it will be "stats".

Optional parameters:
    corr_function: Correlation function used to compute the score at end
                   of the prioritization. Available functions are pearson and
                   spearman correlation. Default (pearson).
        """
        print(help_message)

    def _load_parameters(self, section):
        result = {}
        result['data_path'] = self.config.get(section, 'data_path')
        result['src'] = int(self.config.get(section, 'src'))
        result['dst'] = int(self.config.get(section, 'dst'))
        result['matfile'] = self.config.get(section, 'matfile')
        cross = self.config.get(section, 'fold')
        if cross != '':
            result['fold'] = int(cross)
        result['out'] = self.config.get(section, 'out')
        result['corr_function'] = self.config.get(section, 'corr_function')
        result['mode'] = self.config.get(section, 'mode').lower() 
        
        result['memsave'] = self.config.get(section, 'memsave').lower() in ['yes','true','1']
        result['profile'] = self.config.get(section, 'profile').lower() in ['yes','true','1']
        return result

    def experiment(self, extra_params):
        """
        Run the experiment. All config overriding and stuff are performed
        in the Experiment class.
        """
        self.log.info("Running cross validation..")
        self.log.info("Parsing parameters from config file.")
        
        required = ['matfile', 'src', 'dst']

        if self._are_required_parameters_valid(self.config, required):
            cfg_params = self._load_parameters(self.params_section)

            self.log.info("Loading data...")
            if cfg_params.get('fold', None) is not None:
                ok = validation.verify_numeric_value(cfg_params['fold'],
                                                     'fold', 2, 20, self.log)
                if not ok:
                    self._print_help()
                    return -1

            full_matfile_path = os.path.abspath(os.path.join(cfg_params['data_path'],
                                             cfg_params['matfile']))

            if not validation.check_file_exists(full_matfile_path, self.log):
                print "Exiting"
                return -1

            network_data = graphdata.GraphDataSet.read(cfg_params['data_path'],
                                                       cfg_params['matfile'],
                                                       memsave=cfg_params['memsave'])

            src = cfg_params['src']
            dst = cfg_params['dst']
            mode = cfg_params['mode']

            self.log.info("Performing CV test: {}->{}.".format(src, dst))

            prioritizer = method.ProphNet(network_data)

            prioritizer_test = metrics.PrioritizationTest(prioritizer, self.log)
            prioritizer_test.run_cross_validation(
                src, dst, fold=cfg_params.get('fold', 5),
                out=cfg_params['out'],
                corr_function=cfg_params['corr_function'],
                mode=mode)


            # if cfg_params['memsave']:
            #     self.log.info("Cleaning up tmp files")
            #     prioritizer.graphdata.cleanup_resources()

            self.log.info("Cross validation run successfully.")
            return 0
        else:
            self._print_help()
            return -1
