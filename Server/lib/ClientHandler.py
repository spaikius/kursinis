# -*- coding: utf-8 -*-

import logging
import sys
import json
python3 = sys.version_info >= (3,0)

if python3:
    from . import Workspace
    from . import Voronota
else:
    import Workspace
    import Voronota

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        (self.host, self.port) = addr
        self._bufferSize = 8192
        self.clientHandler()

    def __del__(self):
        pass

    def clientHandler(self):
        """Function for handling client connection."""
        try:
            while True:
                request = self.conn.recv(self._bufferSize).decode()
                logging.info("Client: {}:{} request: {}".format(
                    self.host, self.port, request))
                request = request.split(' ')
                optCode = request[0]

                if optCode == 'CHECKFILE':
                    # request = "opt-code, file-name, checksum"
                    self.handle_file(request[1:])
                elif optCode == 'SENDFILE':
                    # request = "opt-code, file-name"
                    self.handle_send_file(request[1:])
                elif optCode == "GETCGO":
                    # reqest = "opt-code, program, file, *args"
                    self.handle_get(request[1:])
                else:
                    # Client disconect
                    break
                # else:
                #     resp = "BADREQUEST"
                #     self.conn.sendall(resp.encode())
                #     logging.info("Server: Response send to {}:{} response: {}"
                #         .format(self.host, self.port, resp))
                #     break
        except Exception as e:
            logging.critical(e)

        # Close client connection
        self.conn.close()
        logging.info("Server: Conection with {}:{} is closed"
            .format(self.host, self.port))


    def handle_file(self, request):
        """Server FILE. Check if servas has file"""
        file_name = request[0].lower()
        file_size = request[1]
        logging.info("Client: {}:{} requested a CHECKFILE: {} {}".format(
            self.host,self.port,file_name, file_size))

        # check if file exist in server dir
        if Workspace.file_exists(file_name, file_size):
            # EXISTS
            resp = "OK"
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host,self.port,resp))
        else:
            # NO FILE
            resp = "NOTFOUND"
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host,self.port,resp))

    def handle_send_file(self, request):
        """Server PUT. Handles file transfering from client"""
        file_name = request[0].lower()
        logging.info("Client:  {}:{} requested a SENDFILE for: {}".format(
            self.port, self.host, file_name))

        # Send back OK as ACK
        resp = "OK"
        self.conn.sendall(resp.encode())
        logging.info("Server: Response send to {}:{} response: {}".format(
            self.host, self.port, resp))

        # Recieve file size
        fileSize = self.conn.recv(self._bufferSize).decode()
        logging.info("Client: File size: {} bytes".format(fileSize))

        # Send back OK as ACK
        resp = "OK"
        self.conn.sendall(resp.encode())
        logging.info("Server: Response send to {}:{} response: {}".format(
            self.host, self.port, resp))

        # Receive file

        # create file path
        path = Workspace.mkdir(file_name)
        filePath = Workspace.construct_file_path(path, file_name)

        # send file in slices of self._bufferSize bytes:
        # open file in read byte mode:
        fh = open(filePath, "wb") # write bytes flag is passed

        bytes_remaining = int(fileSize)

        while bytes_remaining != 0:
            if(bytes_remaining >= self._bufferSize):
                # receive slab from client
                slab = self.conn.recv(self._bufferSize)
                fh.write(slab)
                sizeof_slab_received = len(slab)
                logging.debug("Server: From {}:{} Bytes received: {} File: {}"
                    .format(self.host, self.port, sizeof_slab_received, file_name))
                bytes_remaining -= int(sizeof_slab_received)
            else:
                #receive slab from server
                slab = self.conn.recv(bytes_remaining)
                fh.write(slab)
                sizeof_slab_received = len(slab)
                logging.debug("Server: From {}:{} Bytes received: {} File: {}".format(
                    self.host, self.port, sizeof_slab_received, file_name))
                bytes_remaining -= int(sizeof_slab_received)
        fh.close()
        resp = "OK"
        self.conn.sendall(resp.encode())
        logging.info("Response send to {}:{} response: {}".format(
            self.host, self.port, resp))

    def handle_get(self, request):
        """Function for handling client GET"""
        file_name = request[0]

        if Workspace.file_exists(file_name):
            # EXISTS
            resp = "OK" # OK
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host,self.port,resp))
        else:
            # NO FILE
            resp = "NOTFOUND"
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host,self.port,resp))
            return

        # Recieve query len
        querylen = self.conn.recv(self._bufferSize).decode()
        logging.info("Server: Query recieved len from {}:{} query len: {}"
            .format(self.host, self.port, querylen))


        # Send OK as ACK
        resp = "OK"
        self.conn.sendall(resp.encode())
        logging.info("Server: Response send to {}:{} response: {}".format(
            self.host, self.port, resp))

        # Recieve query
        bytes_remaining = int(querylen)

        query = ''

        while bytes_remaining != 0:
            if(bytes_remaining >= self._bufferSize):
                # receive slab from client
                slab = self.conn.recv(self._bufferSize).decode()
                query += slab
                sizeof_slab_received = len(slab)
                logging.debug("Client: To {}:{} Bytes sent: {}".format(
                    self.host, self.port, sizeof_slab_received))
                bytes_remaining -= int(sizeof_slab_received)
            else:
                #receive slab from server
                slab = self.conn.recv(bytes_remaining).decode()
                query += slab
                sizeof_slab_received = len(slab)
                logging.debug("Client: To {}:{} Bytes sent: {}".format(
                    self.host, self.port, sizeof_slab_received))
                bytes_remaining -= int(sizeof_slab_received)

        logging.info("Client: Query received from {}:{} query: {}".format(
            self.host, self.port, query))

        success = Voronota.create_contacts_file(file_name)

        # if ClientErr:
        #     resp = "BADQUERY" # Bad request
        #     self.conn.sendall(resp.encode())
        #     logging.info("Response send to {}:{} response: {}".format(
        #         self.host, self.port, resp))

        if not success:
            resp = "SERVERERROR" # Internal server error
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host, self.port, resp))


        query_dict = json.loads(query)
        query = query_dict['_query'].split(' ')
        data = query_dict['data']

        success = Voronota.draw(file_name, query, self.port, data)

        # if ClientErr:
        #     resp = "BADQUERY" # Bad request
        #     self.conn.sendall(resp.encode())
        #     logging.info("Response send to {}:{} response: {}".format(
        #         self.host, self.port, resp))

        if not success:
            resp = "SERVERERROR" # Internal server error
            self.conn.sendall(resp.encode())
            logging.info("Server: Response send to {}:{} response: {}".format(
                self.host, self.port, resp))

        draw_file = Workspace.construct_file_path(
            Workspace.mkdir(file_name), 'draw' + str(self.port))

        # size = Workspace.get_file_size(draw_file)
        size = len(draw_file)

        resp = "OK " + str(size)
        self.conn.sendall(resp.encode())
        logging.info("Server: Response send to {}:{} (FILESIZE) response: {}".format(
            self.host, self.port, resp))

        ack = self.conn.recv(self._bufferSize).decode()
        logging.info("Client: ACK recieved from {}:{} ACK: {}".format(
            self.host, self.port, ack))

        # with open(draw_file, 'r') as fh:
        #         self.conn.sendall(fh.read().encode())

        self.conn.sendall(draw_file.encode())

        logging.info("Server: File has been sent to {}:{}".format(
            self.host, self.port))

        # Workspace.delete_file(draw_file)
