#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import sys

srv_path = os.path.dirname(os.path.realpath(__file__))

if os.name == 'nt': #windwos
    lib_path = os.path.join(srv_path, '.')
    sys.path.insert(0, lib_path) 
else:
    lib_path = os.path.join(srv_path, 'lib')
    sys.path.insert(0, lib_path)

from lib import Config
from lib import Workspace
from lib import TCPServer
from lib import RepeatJob


__author__  = "Rimvydas Noreika"
__credits__ = ["Justas Dapkūnas"]
__version__ = "1.0.1"
__status__  = "Development"


def main():
    
    log_lvl = logging.DEBUG if '--debug' in sys.argv else logging.INFO
   
    # Load configurations
    # Setup logger
    logging.basicConfig(
        filename=Config.LOGGER_FILE,
        format=Config.LOGGER_FORMATTER,
        level=log_lvl)

    # print log info in terminal
    logging.getLogger().addHandler(logging.StreamHandler())

    # Setup root
    Workspace.mkdir_root()
    Workspace.cleanup()
    rj = RepeatJob.RepeatJob(Config.CHECK_FOR_OLD_FILES, Workspace.cleanup)
    rj.start()

    try:
        server = TCPServer.TCPServer(Config.HOST, Config.PORT)
        server.start()
    except Exception as e:
        logging.critical("Can't start the server")
        return

    try:
        print("Server is running. Press Ctrl+C to stop")
        while server.running():
            server.acceptConnection()
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt")
    finally:
        del server
        rj.stop()

if __name__ == '__main__':
    main()
