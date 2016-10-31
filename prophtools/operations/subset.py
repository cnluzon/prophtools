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

..module:: subset.py
..author:: Carmen Navarro Luzón <cnluzon@decsai.ugr.es>

Subsets (randomly or given a set of entities) a given .mat file.

"""
import os

from prophtools.utils import validation
from prophtools.utils.experiment import Experiment

import prophtools.common.graphdata as graphdata

class SubsetGraphExperiment(Experiment):
    """
    Experiment for running a local instance of the prioritization method.
    """
    def _create_default_config(self):
        raise(NotImplementedError("Either trying to use abstract Experiment class or forgot to implement this method"))

    def _load_parameters(self, section):
        params = {}
        params['data_path'] = self.config.get(section, "data_path")
        params['random'] = self.config.get(section, "random").lower() in ['true', 'yes', '1']
        params['size'] = int(self.config.get(section, "size"))
        params['out_file'] = self.config.get(section, "out")
        params['matfile'] = self.config.get(section, "matfile")
        params['entities_file'] = self.config.get(section, "entities_file")
        return params

    def experiment(self, extra_params):
        """
        Run the experiment. All config overriding and stuff are performed
        in the Experiment class.
        """
        self.log.info("Running subset experiment.")
        self.log.info("Parsing from config file.")
        required = ['matfile']

        if self._are_required_parameters_valid(self.config, required):
            cfg_params = self._load_parameters(self.params_section)
            if cfg_params['random']:
                if not validation.verify_natural_number(cfg_params['size'], 'size', self.log):
                    return -1

            elif cfg_params['entities_file']:
                # Select entities from graph data set
                msg = "Selection by entities file not implemented yet. Only random."
                raise NotImplementedError(msg)

            else:
                msg = "Not random selected, nor entities_file provided. Exiting."
                self.log.error(msg)

            full_path_matfile = os.path.join(cfg_params['data_path'], cfg_params['matfile'])

            if not validation.check_file_exists(full_path_matfile, self.log):
                return -1

            matdata = graphdata.load_network_data(cfg_params['data_path'], cfg_params['matfile'])

            if cfg_params['random']:
                self.log.info("Selecting random subset of size {}".format(cfg_params['size']))
                subset = matdata.random_subset(cfg_params['size'])
                subset.write('.', cfg_params['out_file'])

            self.log.info("Subset performed successfully.")
