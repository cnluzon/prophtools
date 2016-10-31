# -*- coding: utf-8 -*-
"""

 .. module :: loggingtools.py
 .. moduleauthor :: C. Navarro Luzón

General functions for initializing logging modules
"""

import logging.config
import os
import json


def init_logging_no_file(log_level):
    # Log file
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S')


def init_generic_log(log_file, log_level):
    # Log file
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filename=log_file,
                        filemode='a')  # append to log


def get_generic_console_handler():
    console = logging.StreamHandler()

    formatter = logging.Formatter('[ %(asctime)s ] %(name)-18s: %(levelname)-8s %(message)s', datefmt='%m/%d %H:%M:%S')
    console.setFormatter(formatter)

    return console


def get_logging_level(verbose_count):
    logging_level = logging.DEBUG
    if (verbose_count < 1):
        logging_level = logging.WARNING
    elif (verbose_count < 2):
        logging_level = logging.INFO

    return logging_level


def init_log_from_file(config_file='../config/logging.json', log_level=logging.DEBUG, env_key='LOG_CFG'):
    """
    Setup logging configuration. Gets the path for logging from environment key LOG_CFG
    """
    log_config_env = os.getenv(env_key, None)
    path = config_file
    if log_config_env:
        path = log_config_env

    if os.path.exists(path):
        with open(path, 'rt') as f:
            
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        init_generic_log('./info.log', log_level)

