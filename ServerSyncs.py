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
import threading
import logging
from configobj import ConfigObj

class SocketFileServer(object):

    def __init__(self, host, port, working_dir):
        self.host = host
        self.port = port
        self.working_dir = working_dir

        if not os.path.exists(working_dir):
            os.mkdir(working_dir)

    def __get_absolute_path(self, src_path):
        """Return absolute path by adding working_dir prefix to `src_path`."""
        return os.path.join(self.working_dir, src_path)

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
                syncs|moved|src_path|dest_path

        """
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.soc.bind((self.host, int(self.port)))
        except socket.error as msg:
            logging.info('Bind failed. Error Code : %s', msg)

        self.soc.listen(10)

        logging.info("listening for connections, on PORT: %s", self.port)
        while 1:
            self.conn, self.addr = self.soc.accept()
            inputready,outputready,exceptready \
                = select.select ([self.conn],[self.conn],[])
            logging.info("Connect by %s", self.addr)
            thread = threading.Thread(target = self.tranfer)
            thread.start()


    def tranfer(self):
        try:
            while True:
                datar = ""
                while 1:
                    data = self.conn.recv(1024)
                    datar += data.decode('utf-8')
                    if len(datar) > 0:
                        break
                logging.info('datar %s', datar)
                datar = datar.split("|")
                if (datar[0] == "syncs" and datar[1] == "moved"): #moved
                    src_path = self.__get_absolute_path(datar[2])
                    dest_path = self.__get_absolute_path(datar[3])
                    if (datar[4] == "1"): #moved directory
                        #if not os.path.exists(dest_path):
                         #   os.makedirs(dest_path)
                        shutil.move(src_path, dest_path)

                    if (datar[4] == "2"): #moved file
                        #copy file src_path to dest_path
                        shutil.move(src_path, dest_path)
                    self.conn.send("moved|ok".encode("utf-8"))


                if (datar[0] == "syncs" and datar[1] == "delete"): #delete
                    src_path = self.__get_absolute_path(datar[2])
                    if os.path.isdir(src_path):
                        shutil.rmtree(src_path)
                    else:
                        #TODO: check if src_path is exist or not
                        if os.path.isfile(src_path):
                            os.remove(src_path)
                    self.conn.send("delete|ok".encode("utf-8"))
                    logging.info("delete success")

                if (datar[0] == "syncs" and datar[1] == "create"): #Create
                    self.conn.send("create|ok".encode("utf-8"))
                    if (datar[2] == "1"): #Create directory
                        dir_path = self.__get_absolute_path(datar[3])
                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)
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
                            file_path = self.__get_absolute_path(datarecv[2])
                            logging.info('Receiving %s', file_path)

                            filesize = int(datarecv[4])
                            logging.info(filesize)

                            self.conn.send("syncs|ok".encode('utf-8'))
                            f = open(file_path, "wb")
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
                            logging.info("Saved file %s", file_path)
        except socket.error as msg:
            logging.info(msg)
            self.conn.close()



    def senddata(self):
        return


class SocketFileClient(object):
    """
    Use as a socket client for sending data.
    """
    def __init__(self, host, port, working_dir):
        self.host = host
        self.port = port
        self.working_dir = working_dir
    def connect(self):
        # initialize socket connection
        is_connect = True
        try:
            self.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sc.connect((self.host, int(self.port)))
        except socket.error as msg:
            logging.info(msg)
            self.sc.close()
            self.sc = None
            is_connect = False
        return is_connect

    def __get_absolute_path(self, src_path):
        """Return absolute path by adding working_dir prefix to `src_path`."""
        return os.path.join(self.working_dir, src_path)

    def on_created(self, src_path, is_directory):
        abs_src_path = self.__get_absolute_path(src_path)

        if is_directory:
            buffsend = "syncs|create|1|" + src_path
            logging.info(buffsend)
            self.sc.send(buffsend.encode('utf-8'))

            buffrecv = self.sc.recv(1024)
            buffrecv = buffrecv.decode('utf-8')
            if (buffrecv == "directory|ok"):
                logging.info("send directory success")

        else:
            buffsend = "syncs|create|2"
            self.sc.send(buffsend.encode("utf-8"))

            buffrecv = self.sc.recv(1024)
            buffrecv = buffrecv.decode('utf-8')
            if (buffrecv == "create|ok"):
                logging.info("create success")

            filesize = os.path.getsize(abs_src_path)
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
                while 1:
                    try:
                        f = open(abs_src_path, "rb")
                        break
                    except IOError as e:
                        logging.info("I/O error({0}): {1}".format(e.errno, e.strerror))
                byteSend = 0
                while 1:
                    if byteSend == filesize:
                        break
                    buff = f.read(1024)
                    self.sc.send(buff)
                    byteSend += len(buff)
            logging.info("Send file success")


    def on_deleted(self, src_path, is_directory):
        buffsend = "syncs|delete|" + src_path
        logging.info(buffsend)
        self.sc.send(buffsend.encode("utf-8"))

        buffrecv = self.sc.recv(1024)
        buffrecv = buffrecv.decode('utf-8')
        if (buffrecv == "delete|ok"):
            logging.info("send directory success")
        else:
            pass


    def on_modified(self, src_path, is_directory):
        if not is_directory:
            self.on_created(src_path, is_directory)
        pass

    def on_moved(self, src_path, dest_path, is_directory):
        if is_directory:
            buffsend = "syncs|moved|%s|%s|1" % (src_path, dest_path)
        else:
            buffsend = "syncs|moved|%s|%s|2" % (src_path, dest_path)

        logging.info(buffsend)
        self.sc.send(buffsend.encode("utf-8"))

        buffrecv = self.sc.recv(1024)
        buffrecv = buffrecv.decode("utf-8")
        if (buffrecv == "moved|ok"):
            logging.info("moved success")
        else:
            pass
        pass