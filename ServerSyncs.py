#-------------------------------------------------------------------------------
# Name:        server
# Purpose:
#
# Author:      hoank PC
#
# Created:     27/10/2014
# Copyright:   (c) hoank PC 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import os.path
import socket
import sys
import select
import json
import logging
from configobj import ConfigObj

class SocketFileServer(object):

    def __init__(self, host, port, working_dir):
        self.host = host
        self.port = port
        self.working_dir = working_dir

        if not os.path.exists(working_dir):
            os.mkdir(working_dir)

    def __real_path(self, src_path):
        """Remove working folder from src_path."""
        return os.sep.join(src_path.split(os.sep)[1:])

    def listen(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((self.host, int(self.port)))
        self.soc.listen(10)

        while True:
            logging.info("listening for connections, on PORT: %s", self.port)
            self.conn, self.addr = self.soc.accept()
            inputready,outputready,exceptready \
                      = select.select ([self.conn],[self.conn],[])
            logging.info("Connect by %s", self.addr)
            datarecv = ""
            while 1:
                data = self.conn.recv(1024)
                datarecv += data.decode('utf-8')
                if len(datarecv) > 0:
                    break

            datarecv = datarecv.split("|")
            if datarecv[0] =="syncs" and datarecv[1] == "filename" and datarecv[3] == "filesize":
                
                # get file name
                file_path = self.__real_path(datarecv[2])

                filesize = int(datarecv[4])

                self.conn.send("syncs|ok".encode('utf-8'))
                f = open(os.path.join(self.working_dir, file_path), "wb")
                byterecv = 0
                while 1:
                    if byterecv == filesize:
                        break
                    buff = self.conn.recv(1024)
                    if len(buff) == 0:
                        break
                    f.write(buff)
                    byterecv += len(buff)
                f.close()
                logging.info("Received file %s", file_path)

    def senddata(self):
        return


class SocketFileClient(object):
    """
    Use as a socket client for sending data.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # initialize socket connection
        self.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sc.connect((host, int(port)))

    def on_created(self, src_path, is_directory):
        if is_directory:
            #TODO: create new directory
            pass
        else:
            filesize = os.path.getsize(src_path)
            datasend = "syncs|filename|" + src_path + "|filesize|" + str(filesize) + "|\r\n"
            
            logging.info(datasend)
            datalen = len(datasend)
            while True:
                lSend = self.sc.send(datasend.encode('utf-8'))
                if lSend == datalen:
                    break
            datarecv = self.sc.recv(1024)
            datarecv = datarecv.decode('utf-8')

            if datarecv == "syncs|ok":
                f = open(src_path, "rb")
                byteSend = 0
                while 1:
                    if byteSend == filesize:
                        break
                    buff = f.read(1024)
                    self.sc.send(buff)
                    byteSend += len(buff)


    def on_deleted(self, src_path, is_directory):
        pass

    def on_modified(self, src_path, is_directory):
        pass

    def on_moved(self, src_path, dest_path, is_directory):
        pass
        








