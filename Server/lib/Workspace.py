# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import logging

from Config import *


def mkdir_root():
    """Creates servers root dir if not exists"""
    if not os.path.exists(SERVER_DIR):
        logging.debug("Creating server root")
        os.mkdir(SERVER_DIR)


def get_file_size(file):
    """Returns size of file"""
    return os.path.getsize(file)


def file_exists(file_name, file_size=None, file_path_FLAG=False):
    """Checks if file exists"""
    mkdir_root()
    if file_path_FLAG:
        return os.path.isfile(file_name) 

    dirPath = os.path.join(SERVER_DIR, file_name)
    if os.path.isdir(dirPath):
        filePath = os.path.join(dirPath, file_name)
        if file_size is None:
            return os.path.isfile(filePath) 
        if os.path.isfile(filePath) and os.path.getsize(filePath) == int(file_size):
            return True

    return False


def mkdir(dir_name):
    """creates directory in servers root dir"""
    mkdir_root()
    dirPath = os.path.join(SERVER_DIR, dir_name)
    if not os.path.isdir(dirPath):
        logging.debug("Creating directory: {}".format(dir_name))
        os.mkdir(dirPath)
    return dirPath


def dir_name(file_path):
    """Returns directory name"""
    return os.path.dirname(file_path)


def construct_file_path(destination, file_name):
    """Constructs file path"""
    return os.path.join(destination, file_name)


def cleanup():
    """Clean up function for removing old directories and content within"""
    logging.debug("Starting clean up")
    if not os.path.exists(SERVER_DIR):
        return
    for dir in os.listdir(SERVER_DIR):
        directory = os.path.join(SERVER_DIR, dir)
        if time.time() - os.stat(directory).st_mtime > OLDER_THAN: 
            if os.path.isdir(directory):
                logging.debug("Removing directory {}".format(directory))
                shutil.rmtree(directory, ignore_errors=True)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.debug("File {} has been deleted".format(file_path))