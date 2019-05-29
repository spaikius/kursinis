# -*- coding: utf-8 -*-
import sys
import os

python3 = sys.version_info >= (3,0)

if python3:
    import configparser
else:
    import ConfigParser as configparser

# --- DEFAULTS ---
# Server
HOST = '127.0.0.1'
PORT = 8888
SERVER_DIR = 'serverWorkSpace'

# Logger
LOGGER_FILE = 'server.log'
LOGGER_FORMATTER = "%(asctime)s:%(levelname)s:%(message)s"

#
CHECK_FOR_OLD_FILES = 86400
OLDER_THAN = 86400

# Program
PROGRAM_PATH = 'voronota'
# program params
COMMAND_ATOMS = 'get-balls-from-atoms-file'
COMMAND_CONTACTS = 'calculate-contacts'
COMMAND_QUERY_CONTACTS = 'query-contacts'
COMMAND_DRAW = 'draw-contacts'
ANNOTATED = '--annotated'
COMMAND_CONTACTS_DRAW = '--draw'
COMMAND_CONTACTS_SIH_DEPTH = '--sih-depth'
COMMAND_CONTACTS_SIH_DEPTH_VAL = '0'
COMMAND_CONTACTS_STEP = '--step'
COMMAND_CONTACTS_STEP_VAL = '1'
COMMAND_QUERY_CONTACTS_GRAPHICS = '--preserve-graphics'
COMMAND_DRAW_PYMOL = '--drawing-for-pymol'


########################################################################
path = os.sep.join((os.path.abspath(__file__).split(os.sep)[:-2]))

config = configparser.ConfigParser()
config.read(os.path.join(path, 'config.ini'))

HOST = config.get('Server', 'HOST')
PORT = config.get('Server', 'PORT')
SERVER_DIR = os.path.join(path, config.get('Server', 'SERVER_DIR'))
LOGGER_FILE = os.path.join(path, config.get('Logger', "LOGGER_FILE"))

if python3:
    LOGGER_FORMATTER = config.get('Logger', "LOGGER_FORMATTER", raw=True)
else:
    LOGGER_FORMATTER = config.get('Logger', "LOGGER_FORMATTER", 1)

CHECK_FOR_OLD_FILES = int(config.get('Cleanup', 'CHECK_FOR_OLD_FILES'))
OLDER_THAN = int(config.get('Cleanup', 'OLDER_THAN'))

PROGRAM_PATH = config.get('Program','PROGRAM_PATH')
