#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   util.py
#
#   These are general methods that are useful throughout the
#   many classes in Amigo.
#

import os
import sys
import yaml
import json
import glob
import logging
import datetime
import jsondiff
import termcolor


def print_to_stderr(msg):
    """
        Send string to STERR and (which is set to the log file)
        and then halts.
    """
    logging.exception(termcolor.colored("{0}".format(msg), 'red'))
    pass


def print_to_stdout(msg, color="white"):
    """
        Send string to STDOUT (which is set to the log file)
    """
    logging.info(termcolor.colored("{0}".format(msg), color))


def get_method_attribute(obj, attr):
    """
        Given an object and a string, return this string as
        an attribute of the object.
    """
    try:
        return getattr(obj, attr)()

    except AttributeError:
         print_to_stderr("Object {0} does not have attribute {1}. Exiting...".format(obj, attr))


def get_diff_dicts(dict1, dict2):
    """
        Given two dictionaries, return the difference
        between then (as a dictionary), or False if
        they are the same dictionary.
    """
    return jsondiff.diff(dict1, dict2, syntax="explicit", dump=True)


def list_files_in_dir(dir_path, ext="*"):
    """
        Return a list of all files found in the directory for a given
        file extension.
    """
    files = []
    search_dir = get_full_path(dir_path, ext)

    for file in glob.glob(search_dir):
        files.append(file)

    return files


def get_date(days_ago=0):
    """
        Return a string with the current date if days=0 or the current
        date minus the number of days.
    """
    date_format = "%Y_%m_%d"
    return (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime(date_format)


def create_dir(dir_path):
    """
        Creates a directory for a given path.
    """
    if not is_path(dir_path):

        os.makedirs(dir_path)
        print_to_stdout("The following directory was created: {0}".format(dir_path))
        return True

    return False


def read_config_file():
    """
       Read config file from local config dir or /opt
    """

    # This is the only hardcoded constant in this repo ;).
    config_file = "./config.yaml"

    if not is_path(config_file):
        print_to_stderr("Error finding {0}. Please set this file and try again.".format(config_file))

    return read_yaml_file(config_file)


def read_yaml_file(yaml_filepath):
    """
        Read a YAML object to a dictionary.
    """
    try:
        with open(yaml_filepath, 'r') as f:
            return yaml.load(f)

    except yaml.YAMLError as e:
        print_to_stderr("Error opening {0}: {1}".format(yaml_filepath, e))


def save_to_json_file(data_dict, filepath, mode="w", pretty=False):
    """
        Save a dictionary object to a JSON file.
    """

    try:
        with open(filepath, mode) as f:
            if pretty:
                json.dump(data_dict, f, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                json.dump(data_dict, f)
                f.write("\n")

        return True

    except IOError as e:
        print_to_stderr("Error saving to {0}: {1}".format(filepath, e))

    except TypeError as e:
        print_to_stderr("Error saving to {0}: {1}".format(filepath, e))


def read_json_file(json_filepath):
    """
        Read a JSON object to a dictionary.
    """
    try:
        with open(json_filepath, 'r') as f:
            return json.load(f)

    except IOError as e:
       print_to_stderr("Error reading from {0}: {1}".format(json_filepath, e))


def is_file(file_path):
    """
        Return True if a file exists for a given path, or halts if False.
    """
    return os.path.isfile(file_path)


def rename_file(file_path_old, file_path_new):
    """
        Return True if a file exists for a given path, or halts if False.
    """
    if is_file(file_path_old):
        os.rename(file_path_old, file_path_new)
        return True

    else:
        print_to_stdout("Could not rename {0} to {1}: File does not exist.".format(file_path_old, file_path_new))
        return False


def is_path(dir_path):
    """
        Return True if a path exists, or halts if False.
    """
    return os.path.exists(dir_path)


def get_basename_file(filename):
    """
        Given a path for a file, returns the name of the file.
    """
    return os.path.basename(filename)


def extract_resource_info(filepath):
    """
        Given a file path to a report, extract the name of the resource
        and the attribute being reported, returning them as two strings.
        Note that `@` was defined as the separator when the report was
        saved in disk.
    """
    try:
        data = os.path.splitext(os.path.basename(filepath))[0].split("@")
        return data[0], data[1]

    except KeyError as e:
        print_to_stderr("Error extracting resource info from {filepath}: {1}".format(json_filepath, e))


def get_full_path(dir_path, file):
    """
        Given a directory and a file, return the full UNIX path.
    """
    return os.path.join(dir_path, file)


def get_value(dictionary, key):
    """
        Returns the value of a key in a dictionary or raise an error
        if the key does not exist.
    """
    if key in dictionary:
        return dictionary[key]

    print_to_stderr("Key {0} does not exist in the data. Exiting...".format(key))


def jsonfy(string):
    """
        Make a string becomes a JSON object.
    """
    string = string or ""
    try:
        return json.loads(string)

    except ValueError as e:
        print_to_stderr("Cannot load {0} to JSON.".format(string))

    except TypeError as e:
        print_to_stderr("Cannot jsonfy {0}.".format(string))

