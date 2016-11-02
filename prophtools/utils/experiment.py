# -*- coding: latin-1 -*-

"""
 .. module:: experiment.py
 .. moduleauthor:: C. Navarro Luzón

"""

import logging
import ConfigParser
import os
import cProfile
import pstats
import StringIO


class Experiment:
    """
    Abstract class that creates a log, takes a config and overrides config
    values with console arguments. After running the experiment (children
    classes will perform it), it writes on exp_name_overridden.cfg the
    configuration used for running, including information about overridden
    parameters.

    It is an abstract class. Any class that inherits from it must implement
    an experiment() method.

    Args:
        config_file:  File where the config values are read from.
        exp_name:     Name of the experiment.
        log:          Logger object (or None)
        section_name: If the config_file has several sections, which one to get
                      arguments from.
    """
    def __init__(self, config_file, exp_name, log, section_name=None):
        self.exp_name = exp_name
        self.default_config_file = "./config/configTemplate.cfg"
        self.log = log or logging.getLogger(__name__)
        self.alternative_out_cfg = False
        self.profiler = cProfile.Profile()

        self.params_section = "simulation_parameters"
        if section_name:
            self.params_section = section_name

        if config_file:
            self.config = ConfigParser.ConfigParser()
            self.config.read(config_file)
            self.config_file = config_file

        else:
            self._set_default_values(self.default_config_file)
            self.config_file = self.default_config_file

    def _start_profiling(self):
        self.profiler.enable()

    def _end_profiling(self):
        self.profiler.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(self.profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        return s.getvalue()

    def _set_default_values(self, config_file):

        if config_file:
            parser = ConfigParser.ConfigParser()
            self.config = parser.read(config_file)
        else:
            self.config = self._create_default_config()

    def _override_config_values(self, parameter_dict):
        try:
            self.config.add_section("{}_overridden".format(self.params_section))
        except ConfigParser.DuplicateSectionError:
            warning_msg = ("Tried to override an already overriden config! "
                           "Results will be written in a copy %s_2.cfg file"
                           % self.exp_name)

            self.log.warning(warning_msg)
            self.alternative_out_cfg = True

        for key, value in parameter_dict.iteritems():
            self.log.debug("Overriding config value %(key)s to %(value)s" %
                           {"key": key, "value": value})

            try:
                overriden_value = (self.config.get(self.params_section, key))
            except ConfigParser.NoOptionError:
                overriden_value = ""

            self.config.set(self.params_section, key, value)

            self.config.set("{}_overridden".format(self.params_section),
                            key,
                            overriden_value)

    def _write_config(self):
        filename = "%s.cfg" % self.exp_name
        if self.alternative_out_cfg:
            filename = self.exp_name + "_2.cfg"
        config_out = open(filename, "w")

        self.log.debug("Writing config file: {} in directory {}".format(
            filename,
            os.path.dirname(filename)))

        self.config.write(config_out)
        self.overriden_config_path = os.path.abspath(filename)

    def run(self, override_list, extra_params, override_dict=None):
        exp_result = None
        parameter_dict = {}
        if override_dict:
            parameter_dict = override_dict
        else:
            parameter_dict = self._generate_dict(override_list)
        self._override_config_values(parameter_dict)
        self._write_config()
        print "HOLI"
        exp_result = self.experiment(extra_params)
        return exp_result

    def print_config_values(self):
        sections = self.config.sections()
        for s in sections:
            print "[%s]" % s
            for key, value in self.config.items(s):
                print key, value

    def _generate_dict(self, param_list):
        result = {}
        for i in range(len(param_list) - 1):
            if param_list[i][0] == '-' and param_list[i][1] == '-':
                result[param_list[i].lstrip('-')] = param_list[i+1]

        return result

    def _are_required_parameters_valid(self, config, required):
        missing_parameters = []
        for param in required:
            try:
                parameter = config.get(self.params_section, param)
                if parameter == '':
                    missing_parameters.append(param)
            except ConfigParser.NoOptionError:
                missing_parameters.append(param)

        if missing_parameters:
            msg = self._missing_parameters_msg(missing_parameters)
            self.log.error(msg)
            return False

        return True

    def _missing_parameters_msg(self, missing):
        missing_str = ', '.join(missing)
        msg = 'Cannot properly run this experiment, missing parameters: {}'.format(missing_str)
        return msg
