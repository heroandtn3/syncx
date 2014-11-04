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
import shutil
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
        """
        server listen host and port
        app: Signature is "syncs"
        buffer recv:
            create: Create file
                create|1|: directory "syncs|create|1|directory"
                create|2|: file      "syncs|create|2|"
            delete: Delete file
                syncs|delete|directory
            modifed: modifed file
                syncs|modifed|1|directory
                syncs|modifed|2|file
            moved: moved file
                syncs|moved|1|directory
                syncs|moved|2|file


        """
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((self.host, int(self.port)))
        self.soc.listen(10)

        logging.info("listening for connections, on PORT: %s", self.port)
        self.conn, self.addr = self.soc.accept()
        inputready,outputready,exceptready \
            = select.select ([self.conn],[self.conn],[])
        logging.info("Connect by %s", self.addr)

        while True:
            datar = ""
            while 1:
                data = self.conn.recv(1024)
                datar += data.decode('utf-8')
                if len(datar) > 0:
                    break
            logging.info(datar)
            datar = datar.split("|")

            if (datar[0] == "syncs" and datar[1] == "delete"): #delete
                if os.path.isdir(os.path.join(self.working_dir, datar[2])):
                    shutil.rmtree(os.path.join(self.working_dir, datar[2]))
                else:
                    os.remove(os.path.join(self.working_dir, datar[2]))
                self.conn.send("delete|ok".encode("utf-8"))
                logging.info("delete success")

            if (datar[0] == "syncs" and datar[1] == "create"): #Create
                if (datar[2] == "1"): #Create directory
                    if not os.path.exists(os.path.join(self.working_dir, datar[3])):
                        os.makedirs(os.path.join(self.working_dir, datar[3]))
                    logging.info("Create directory success")
                    self.conn.send("directory|ok".encode("utf-8"));
                if (datar[2] == "2"): #Create file
                    logging.info("Create file")
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
                        logging.info(file_path)

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
            directory = src_path[src_path.find("\\") + 1 : len(src_path)]
            buffsend = "syncs|create|1|" + directory
            logging.info(buffsend)
            self.sc.send(buffsend.encode('utf-8'))

            buffrecv = self.sc.recv(1024)
            buffrecv = buffrecv.decode('utf-8')
            if (buffrecv == "directory|ok"):
                logging.info("send directory success")

        else:
            buffsend = "syncs|create|2"
            self.sc.send(buffsend.encode("utf-8"))

            filesize = os.path.getsize(src_path)
            datasend = "syncs|filename|" + src_path + "|filesize|" + str(filesize)

            logging.info(datasend)
            datalen = len(datasend)
            while True:
                lSend = self.sc.send(datasend.encode('utf-8'))
                if lSend == datalen:
                    break
            datarecv = self.sc.recv(1024)
            datarecv = datarecv.decode('utf-8')

            logging.info(datarecv)
            if datarecv == "syncs|ok":
                f = open(src_path, "rb")
                byteSend = 0
                while 1:
                    if byteSend == filesize:
                        break
                    buff = f.read(1024)
                    self.sc.send(buff)
                    byteSend += len(buff)
            logging.info("Send file success")


    def on_deleted(self, src_path, is_directory):
        directory = src_path[src_path.find("\\") + 1 : len(src_path)]
        buffsend = "syncs|delete|" + directory
        logging.info(buffsend)
        self.sc.send(buffsend.encode("utf-8"))

        buffrecv = self.sc.recv(1024)
        buffrecv = buffrecv.decode('utf-8')
        if (buffrecv == "delete|ok"):
            logging.info("send directory success")
        else:
            pass


    def on_modified(self, src_path, is_directory):

        pass

    def on_moved(self, src_path, dest_path, is_directory):
        pass









