# -*- coding: latin-1 -*-

"""
Prophtools: Tools for heterogenoeus network prioritization.

Copyright (C) 2016 Carmen Navarro Luzón <cnluzon@decsai.ugr.es>

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

 .. module :: run.py
 .. moduleauthor :: C. Navarro Luzón <cnluzon@decsai.ugr.es>

 Runs a Prioritization query on sample data or a provided matrix file.

"""
import prophtools.common.method as method
import prophtools.common.graphdata as graphdata
import prophtools.utils.validation as validation

from prophtools.utils.experiment import Experiment

import os


class LocalRunExperiment(Experiment):
    """
    Experiment for running a local instance of the prioritizationmethod.
    """
    def _print_help(self):
        help_message = """
ProphTools prioritize: Run a local prioritization experiment on a network
configuration.

Required parameters:
    matfile: mat file containing the networks and their configuration (see
             ProphTools documentation for more info on this format.)
    src    : Source network (as an index)
    dst    : Destination network (as an index)
    qindex : Comma-separated list of indexes that are on the query target.
    qname  : Comma-separated list of IDs of the nodes in the query target.

Optional parameters:
    corr_function: Correlation function used to compute the score at end
                   of the prioritization. Available functions are pearson and
                   spearman correlation (Default: pearson).
    n            : Number of results to show on screen (Default: 10).
    out          : Output csv file with the prioritization results (Default: none).
    memsave      : Run ProphTools in a memory save mode. This is recommended for
                   large networks. (Default: False).

        """
        print(help_message)


    def _run_prioritizer(self, prioritizer, idx_query, origin, destination,
                         method="prophnet", corr_function="pearson", profile=False):
        """
        A helper method for the experiment routine.
        """
        self._start_profiling()
        results = prioritizer.propagate(idx_query,
                                        origin,
                                        destination,
                                        corr_function)

        stats = self._end_profiling()

        if profile:
            print stats

        sorted_results = sorted(results, key=lambda x: x[0], reverse=True)

        return sorted_results
        
    def _print_formatted_results(self, results, method, max_results):
        top_results = min(len(results), max_results)
        print "Entity\tScore"
        for i in range(top_results):
            result_entity = results[i][1]
            result_score = results[i][0]

            result_str = '{}\t{:8.4f}'.format(result_entity, result_score)
            print result_str

    def _save_to_file(self, out, results):
        fo = open(out, 'w')
        fo.write('Entity,Score\n')
        for r in results:
            result_str = '{},{:8.4f}'.format(r[1], r[0])
            fo.write(result_str + '\n')

        fo.close()

    def _load_parameters(self, section):
        params = {}
        params['data_path'] = self.config.get(section, 'data_path')
        params['src'] = int(self.config.get(section, 'src'))
        params['dst'] = int(self.config.get(section, 'dst'))
        params['matfile'] = self.config.get(section, 'matfile')
        params['corr_function'] = self.config.get(section, 'corr_function')
        params['qindex'] = self.config.get(section, 'qindex')
        params['qname'] = self.config.get(section, 'qname')
        params['out'] = self.config.get(section, 'out')
        params['n'] = int(self.config.get(section, 'n'))
        params['memsave'] = self.config.get(section, 'memsave').lower() in ['yes','true','1']
        params['profile'] = self.config.get(section, 'profile').lower() in ['yes','true','1']
        return params

    def exit(self, prioritizer, memsave=False, exit_code=-1):

        if memsave:
            self.log.info("Cleaning up graph resources.")
            prioritizer.graphdata.cleanup_resources()

        self.log.info("Exiting")

    def experiment(self, extra_params):
        """
        Run the experiment. All config overriding and stuff are performed
        in the Experiment class.
        """
        self.log.info("Running Prioritization.")
        self.log.info("Parsing parameters from config file.")
        required = ['matfile', 'src', 'dst']
        if self._are_required_parameters_valid(self.config, required):
            cfg_params = self._load_parameters("run")

            self.log.info("Loading data.")

            propagation_data = None
            matfile_path = os.path.join(cfg_params['data_path'],
                                        cfg_params['matfile'])

            if validation.check_file_exists(matfile_path, self.log):
                propagation_data = graphdata.GraphDataSet.read(
                    cfg_params['data_path'],
                    cfg_params['matfile'], memsave=cfg_params['memsave'])
            else:
                msg = "Could not open matfile {}. Exiting.".format(matfile_path)
                self.log.error(msg)
                return -1
            
            prioritizer = method.ProphNet(propagation_data)

            query_index_vector = []
            if cfg_params['qindex']:
                query_index_vector = cfg_params['qindex'].split(',')
            elif cfg_params['qname']:
                query_name_vector = cfg_params['qname'].split(',')
                for q in query_name_vector:
                    names = list(prioritizer.graphdata.networks[cfg_params['src']].node_names)
                    names = [i.lower().strip() for i in names]
                    try:
                        ind = names.index(q)
                        query_index_vector.append(ind)
                    except ValueError:
                        self.log.warning("Query ID {} not found in src network.".format(q))

                if query_index_vector == []:
                    self.log.error("Empty query. Exiting.")
                    self.exit(prioritizer, memsave=cfg_params['memsave'])
                    return -1
            else:
                self.log.error("No indices or names provided as query.")
                self.exit(prioritizer, memsave=cfg_params['memsave'])
                return -1

            query_vector = [int(q) for q in query_index_vector]

            self.log.info("Prioritizing.")

            sorted_results = self._run_prioritizer(prioritizer, query_vector,
                                  cfg_params['src'],
                                  cfg_params['dst'],
                                  corr_function=cfg_params['corr_function'],
                                  profile=cfg_params['profile'])

            self._print_formatted_results(sorted_results, "prophnet", cfg_params['n'])

            if cfg_params['out']:
                self.log.info("Saving output to file {}".format(cfg_params['out']))
                self._save_to_file(cfg_params['out'], sorted_results)
        
            if cfg_params['memsave']:
                self.log.info("Cleaning up tmp files")
                prioritizer.graphdata.cleanup_resources()

            self.log.info("Experiment run successfully.")
            return 0

        else:
            self._print_help()
            return -1
