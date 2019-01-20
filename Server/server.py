# -*- coding: utf-8 -*-

import os
import logging
import sys

# sys.path.insert(0, 'lib')

from lib import Config
from lib import Workspace
from lib import TCPServer
from lib import RepeatJob


__author__  = "Rimvydas Noreika"
__credits__ = ["Justas Dapkūnas"]
__version__ = "1.0.1"
__status__  = "Development"


def main():
    if len(sys.argv) != 1 and sys.argv[1] == '--debug':
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO


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
        logging.critical("On server startup: {}".format(e.message))
        sys.exit()

    try:
        print("Server is running. Press Ctrl+C to stop")
        while server.running():
            server.acceptConnection()
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt")
    finally:
        server.shutdown()
        rj.stop()

if __name__ == '__main__':
    main()
