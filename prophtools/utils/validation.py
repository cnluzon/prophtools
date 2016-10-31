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


def generate_dict_from_remainder(param_list):
    result = dict()
    for i in range(len(param_list) - 1):
        if param_list[i][0] == '-' and param_list[i][1] == '-':
            result[param_list[i].lstrip('-')] = param_list[i+1]

    return result


def remove_repeated(args_list, log):
    no_repeats_list = []
    no_repeats_key_list = []

    for i in range(len(args_list) - 1):
        if args_list[i][0:2] == '--':
            key = args_list[i].lstrip('-')
            if key not in no_repeats_key_list:
                no_repeats_key_list.append(key)
                no_repeats_list.append(args_list[i])
                no_repeats_list.append(args_list[i+1])
            else:
                log.warning("Repeated key " + key + " new value " + args_list[i+1] + " will be ignored")
        elif args_list[i][0] == '-':
            log.warning("Only -- optional args used to override. Found " + args_list[i] + " key, will be removed.")

    if args_list:
        if args_list[-1][0:1] == '--':
            last_key = args_list[-1].lstrip('-')
            if last_key not in no_repeats_key_list:
                no_repeats_key_list.append(last_key)
                no_repeats_list.append(args_list[-1])

            else:
                log.warning("Repeated key " + key + " new value " + args_list[i+1] + " will be ignored")

    log.debug(str(no_repeats_list))
    return no_repeats_list


def validate_overridden_values(overriden, optional_args_list, log):

    for a in optional_args_list:
        if a in overriden:
            warning_msg = ("Found optional value %s in the arguments to override. "
                           "Results could be affected. To solve this at the moment, "
                           "put the optional arguments before the positional ones. " % str(a)
                           )
            log.warning(warning_msg)
    # override_dict = generate_dict(args.override)

    for a in overriden:
        if re.match('-v+', a):
            warning_msg = ("Verbosity count found in the arguments to override. "
                           "If this is an error, you might not see verbosity output. "
                           "Please put your %s before the positional arguments. " % str(a)
                           )
            log.warning(warning_msg)

    remove_repeated(overriden, log)


def get_file_directory(filename):
    return os.path.realpath(filename)


def strip_file_directory(filename):
    return os.path.basename(filename)
