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
