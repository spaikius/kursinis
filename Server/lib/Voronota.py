# -*- coding: utf-8 -*-

import subprocess
import logging
import tempfile
import os
import sys
import re

from collections import defaultdict

python3 = sys.version_info >= (3,0)

if python3:
    from . import Workspace
    from .Config import *
else:
    import Workspace
    from Config import *

def create_contacts_file(file_name):
    """Creates contacts file"""
    # get paths
    path = Workspace.mkdir(file_name)
    pdb_file = Workspace.construct_file_path(path, file_name)
    contacts_file = Workspace.construct_file_path(path, 'contacts')

    if Workspace.file_exists(contacts_file,file_path_FLAG=True):
        return True

    try:
        with open(pdb_file, 'r') as file:
            pipe = subprocess.Popen([
                PROGRAM_PATH,
                COMMAND_ATOMS,
                ANNOTATED
                ], stdin=file, stdout=subprocess.PIPE)

        with open(contacts_file, 'w') as fh:
            pipe2 = subprocess.Popen([
                PROGRAM_PATH,
                COMMAND_CONTACTS,
                ANNOTATED,
                COMMAND_CONTACTS_DRAW,
                COMMAND_CONTACTS_SIH_DEPTH,
                COMMAND_CONTACTS_SIH_DEPTH_VAL,
                COMMAND_CONTACTS_STEP,
                COMMAND_CONTACTS_STEP_VAL
                ], stdin=pipe.stdout, stdout=fh)
            pipe2.wait()
            
    except Exception as e:
        logging.error("Creating contacts: {}".format(e))
        return False

    logging.debug("Contacts file in {} has been created".format(path))
    # return (True, None)ALPHA
    return True

def draw(file_name, query, ID, params):
    path = Workspace.mkdir(file_name)
    contacts_file = Workspace.construct_file_path(path, 'contacts')

    draw_file = Workspace.construct_file_path(path, 'draw' + str(ID))

    query = query.split(' ')
    filters = list(params['query'].keys())
    drawing = list()
    [drawing.extend([str(k),str(v)]) for k,v in params['drawing'].items()]
    
    # try:
    file = open(contacts_file)

    pipe = subprocess.Popen([
        PROGRAM_PATH,
        COMMAND_QUERY_CONTACTS,
        COMMAND_QUERY_CONTACTS_GRAPHICS,
        ]+query+filters, stdin=file, stdout=subprocess.PIPE) #stdout=subprocess.PIPE)

    devnull = open(os.devnull, 'w')

    pipe2 = subprocess.Popen([
        PROGRAM_PATH,
        COMMAND_DRAW,
        '--drawing-name',
        'vcontacts_' + str(ID),
        COMMAND_DRAW_PYMOL,
        draw_file,
        ]+drawing, stdout=devnull, stdin=pipe.stdout)
    pipe2.wait()
    
    return True

def summarize(file_name, query):
    path = Workspace.mkdir(file_name)
    contacts_file = Workspace.construct_file_path(path, 'contacts')
    query = query.split(' ')
    try:
        file = open(contacts_file)

        pipe = subprocess.Popen([
            PROGRAM_PATH,
            COMMAND_QUERY_CONTACTS,
            '--summarize-by-first'
            ]+query, stdin=file,stdout=subprocess.PIPE) #stdout=subprocess.PIPE)


        summary = defaultdict(int)
        for line in iter(pipe.stdout.readline, ''):
            line = line.decode().strip()
            if not line:
                break
            data = line.split(" ")
            m = re.search('c<(.*?)>', data[0])
            summary[m.group(1)] +=  float(data[2])

    except Exception as e:
        logging.error(e)
        return False
    return summary
