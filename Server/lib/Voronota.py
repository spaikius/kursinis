# -*- coding: utf-8 -*-

import subprocess
import logging
import tempfile
import os

from Config import *
import Workspace


def create_contacts_file(file_name):
    """Creates contacts file"""
    # get paths
    path = Workspace.mkdir(file_name)
    pdb_file = Workspace.construct_file_path(path, file_name)
    contacts_file = Workspace.construct_file_path(path, 'contacts')

    # how to be sure if file is not modified? HASH STRING? 
    if Workspace.file_exists(contacts_file,file_path_FLAG=True):
        return True

    try:
        with open(pdb_file, 'rb') as file:
            # ATOMS
            pipe = subprocess.Popen([
                PROGRAM_PATH,
                COMMAND_ATOMS,
                ANNOTATED
                ], stdin=file, stdout=subprocess.PIPE)

            # if pipe.stderr:
            #     logging.error("Standard error in {} {} err: {}".format(
            #         PROGRAM_PATH, COMMAND_ATOMS, pipe.stderr))
            #     print pipe.stderr
            #     return (False, pipe.stderr)

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
            # if pipe2.stderr:
            #     logging.error("Standard error in {} {} err: {}".format(
            #         PROGRAM_PATH, COMMAND_CONTACTS, pipe2.stderr))
            #     return (False, pipe.stderr)
    
    except Exception as e:
        logging.error(e)
        # return (False, None)
        return False
    
    logging.debug("Contacts file in {} has been created".format(path))
    # return (True, None)ALPHA
    return True

def draw(file_name, query, ID):
    path = Workspace.mkdir(file_name)
    contacts_file = Workspace.construct_file_path(path, 'contacts')
    
    draw_file = Workspace.construct_file_path(path, 'draw' + str(ID))

    random_colors = ''
    if query[0] == '--random-colors':
        random_colors = query.pop(0)

    try:
        file = open(contacts_file)
        pipe = subprocess.Popen([
            PROGRAM_PATH,
            COMMAND_QUERY_CONTACTS,
            COMMAND_QUERY_CONTACTS_GRAPHICS,
            ]+query, stdin=file,stdout=subprocess.PIPE) #stdout=subprocess.PIPE)

        # if pipe.stderr:
        #     logging.error("Standard error in {} {} err: {}".format(
        #         PROGRAM_PATH, COMMAND_CONTACTS, pipe2.stderr))
        #     return (False, pipe.stderr)
        
        devnull = open(os.devnull, 'w')
             
        pipe2 = subprocess.Popen([
            PROGRAM_PATH,
            COMMAND_DRAW,
            random_colors,
            COMMAND_DRAW_OPACITY,
            COMMAND_DRAW_OPACITY_VAL,
            COMMAND_DRAW_PYMOL,
            draw_file,
            ], stdout=devnull, stdin=pipe.stdout)
        pipe2.wait()
        # if pipe2.stderr:
        #     logging.error("Standard error in {} {} err: {}".format(
        #         PROGRAM_PATH, COMMAND_CONTACTS, pipe2.stderr))
        #     return (False, pipe2.stderr)

    except Exception as e:
        logging.error(e)
        # return (False, None)
        return False
    # return (True, None)
    return True
