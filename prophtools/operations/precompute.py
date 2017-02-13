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

..module:: precompute.py
..author:: Carmen Navarro Luzón <cnluzon@decsai.ugr.es>

Replaces a matrix in a mat file for its normalized and adds the precomputed
matrix to the same file.

"""
from prophtools.utils.experiment import Experiment
import prophtools.utils.preprocessing as preprocessing
import scipy.io as sio


class NormalizePrecomputeExperiment(Experiment):
    """
    Experiment for taking a raw matrix in a mat file, normalize it and add 
    precomputed matrix to the same result file.
    """
    def _create_default_config(self):
        error_msg = "Either trying to use abstract Experiment class or forgot to implement this method"
        raise(NotImplementedError(error_msg))

    def _load_parameters(self, section):
        params = {}
        params['key'] = self.config.get(section, "key")
        params['matfile'] = self.config.get(section, "matfile")
        params['normalized'] = self.config.get(section, "normalized").lower() in ['true', '1', 'yes']
        return params

    def experiment(self, extra_params):
        """
        Run the experiment. All config overriding and stuff are performed
        in the Experiment class.
        """
        self.log.info("Running subset experiment.")
        self.log.info("Parsing from config file.")
        required = ['matfile', 'key']

        if self._are_required_parameters_valid(self.config, required):
            cfg_params = self._load_parameters(self.params_section)
            matfile_content = sio.loadmat(cfg_params['matfile'])
            mat_id = cfg_params['key']

            normalized_matrix = None
            if not cfg_params['normalized']:
                self.log.info("Normalizing matrix")
                normalized_matrix = preprocessing.normalize_matrix(matfile_content[mat_id])
            else:
                self.log.info("Matrix already normalized")
                normalized_matrix = matfile_content[mat_id]

            self.log.info("Precomputing matrix")
            precomputed_matrix = preprocessing.precompute_matrix(normalized_matrix)

            mat_id_precomputed = '{}_precomputed'.format(mat_id)
            matfile_content[mat_id] = normalized_matrix
            matfile_content[mat_id_precomputed] = precomputed_matrix

            self.log.info("Overwriting matrix file with precomputed and normalized matrices")
            sio.savemat(cfg_params['matfile'], matfile_content)
