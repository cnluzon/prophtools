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

..module:: preprocessxml.py
..author:: Carmen Navarro Luzón <cnluzon@decsai.ugr.es>

Converts a GEXF XML file to a .mat file with precomputed matrices. This step
is required to use prophtools as prioritizer.

"""
from prophtools.utils.experiment import Experiment
import prophtools.utils.preprocessing as preprocessing
import scipy.io as sio
import prophtools.utils.graphio as graphio

class PreprocessXMLExperiment(Experiment):
    """
    Experiment for taking a raw matrix in a mat file, normalize it and add 
    precomputed matrix to the same result file.
    """
    def _create_default_config(self):
        error_msg = "Either trying to use abstract Experiment class or forgot to implement this method"
        raise(NotImplementedError(error_msg))

    def _load_parameters(self, section):
        params = {}
        params['xmlfile'] = self.config.get(section, "xmlfile")
        params['precompute'] = self.config.get(section, "precompute").lower() in ['true', '1', 'yes']
        params['out'] = self.config.get(section, "out")
        params['data_path'] = self.config.get(section, "data_path")
        return params

    def experiment(self, extra_params):
        """
        Run the experiment. All config overriding and stuff are performed
        in the Experiment class.
        """
        self.log.info("Running preprocess xml experiment.")
        self.log.info("Parsing from config file.")
        required = ['xmlfile', 'out', 'precompute']

        if self._are_required_parameters_valid(self.config, required):
            cfg_params = self._load_parameters(self.params_section)
            xmlfile = cfg_params['xmlfile']
            outfile = cfg_params['out']
            cfg_precompute = cfg_params['precompute']
            path = cfg_params['data_path']

            self.log.info("Reading GEXF file format")
            graph = graphio.load_graph(xmlfile)

            self.log.info("Converting to ProphTools format")
            converted = graphio.convert_to_graphdataset(graph, precompute=cfg_precompute)

            self.log.info("Writing mat file")
            converted.write(path, outfile)

            self.log.info("Process performed successfully")
            return 0

        else:
            self.log.error("Exiting")
            return -1
