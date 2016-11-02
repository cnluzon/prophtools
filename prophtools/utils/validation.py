"""
 ..module:: validation.py
 ..moduleauthor::  Carmen Navarro <cnluzon@decsai.ugr.es>

 Helper functions for script validation
"""

import os
import re


def check_file_exists(filename, log=None):
    if os.path.isfile(filename):
        return True
    else:
        if log:
            msg = "File {} does not exist".format(filename)
            log.error(msg)

        return False


def try_to_open_file(filename, log):
    try:
        with open(filename):
            log.info("File " + filename + " opened successfully")
    except IOError:
        log.error("Unable to open input file " + filename)

    return


def verify_natural_number(v, vName, log):
    return verify_numeric_value_over_value(v, vName, 0, log)


def verify_numeric_value_over_value(v, vName, minVal, log):
    if v <= minVal:
        msg = "Invalid {} value. Must be a number higher than {}".format(vName, minVal)
        log.error(msg)
        return False

    return True


def verify_numeric_value(v, vName, minVal, maxVal, log):
    is_ok = True
    if ((v < minVal) or (v > maxVal)):
        is_ok = False

    if not is_ok:
        log.error("Invalid " + vName + " value: Must be a number between " + str(minVal) + " and " + str(maxVal) + ".")

    return is_ok


def check_extension(filename, ext):
    """
    Checks if filename has the corresponding extension.
    """
    last_dot = filename.rfind('.')
    if last_dot > 1:
        if filename[last_dot+1:] == ext:
            return True
        else:
            return False
    elif not ext:
        return True     # If no dot and no ext, file has no extension

def get_file_directory(filename):
    return os.path.realpath(filename)


def strip_file_directory(filename):
    return os.path.basename(filename)
