# -*- coding: utf-8 -*-

import socket
import time
import logging
import sys

python3 = sys.version_info >= (3,0)

if python3:
    from _thread import start_new_thread
else:
    from thread import start_new_thread

import ClientHandler

class TCPServer:
    def __init__(self, host, port):
        try:
            self.address = (host, int(port))
        except ValueError:
            raise ValueError("Port number must be numeric")
        self._serv_socket = None
        self._acpt_conn_num = 10
        self._running = False

    def start(self):
        """Function for initializing, binding server socket and
        starts listening for connections"""
        try:
            self._serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._serv_socket.bind(self.address)
        except socket.error as msg:
            logging.critical("Can't create socket. Error code: {}, Msg: {}".format(*msg))
            raise

        self._serv_socket.listen(self._acpt_conn_num)
        self._running = True
        logging.info("Socket created, binded and now listening")

    def running(self):
        return self._running

    def acceptConnection(self):
        """Function for accepting client connections.
        Function creates a new thread and passes client socket to clientHandler"""
        client_conn, client_addr = self._serv_socket.accept()
        logging.info("Connected with: {}:{}".format(*client_addr))
        try:
            tid = start_new_thread(ClientHandler.ClientHandler, (client_conn, client_addr))
            logging.debug("Thread created. ID: {}".format(tid))
        except Exception as e:
            logging.error("Lost connection with client. msg: {}".format(e))

    def shutdown(self):
        """Server shutdown function"""
        self._serv_socket.shutdown(socket.SHUT_RDWR)
        self._serv_socket.close()
        self._running = False
        logging.info("Server Shutdown")
