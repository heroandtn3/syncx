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
import time
from socket import error
import shutil
import sys
import select
import json
import threading
import logging
from configobj import ConfigObj
import syncscrypto

class SocketListener(object):
 
    def on_connect(self):
        """Call when socket connect or reconnect."""
        pass
 
    def on_disconnect(self):
        """Call when socket is disconnected."""
        pass

class SocketFileClient(object):

    def __init__(self, host, port, working_dir,  socket_listener = None):
        self.host = host
        self.port = port
        self.working_dir = working_dir
        self.crypto = syncscrypto.SyncsCrypto()
        self.rsa = self.crypto.rsa_loadkey()

        if socket_listener is None:
            self.socket_listener = SocketListener()
        else:
            self.socket_listener = socket_listener

        if not os.path.exists(working_dir):
            os.mkdir(working_dir)

    def __get_absolute_path(self, src_path):
        """Return absolute path by adding working_dir prefix to `src_path`."""
        return os.path.join(self.working_dir, src_path)

    def connect(self):
        # initialize socket connection
        is_connect = True
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.host, int(self.port)))
            self.socket_listener.on_connect()
            thread = threading.Thread(target = self.tranfer)
            thread.start()

        except socket.error as msg:
            logging.info(msg)
            self.conn.close()
            is_connect = False
        return is_connect


    def tranfer(self):
        is__disconnect = False

        try:
            while not is__disconnect:
                datar = ""
                while 1:
                    data = self.conn.recv(1024)
                    
                    #if data = "" then client disconnect
                    if not data:
                        logging.info("Client disconnect from: %s"%self.conn)
                        self.conn.close()
                        self.socket_listener.on_disconnect()
                        is__disconnect = True
                        break
                    datar += data.decode('utf-8')
                    if len(datar) > 0:
                        break
                if is__disconnect:
                    break

                #logging.info('datar %s', datar)
                buffr = datar
                datar = datar.split("|")

                if datar[0] == "Signature": #verify
                    dataenc = buffr[len(datar[0]) + 1 : len(buffr)]
                    logging.info(s)
                    datadec = self.crypto.rsa_decrypt(dataenc, self.rsa)
                    logging.info(dataenc)


                if (datar[0] == "syncs" and datar[1] == "moved"): #moved
                    src_path = self.__get_absolute_path(datar[2])
                    dest_path = self.__get_absolute_path(datar[3])
                    if (datar[4] == "1"): #moved directory
                        if os.path.isdir(src_path):
                            shutil.move(src_path, dest_path)

                    if (datar[4] == "2"): #moved file
                        #copy file src_path to dest_path
                        if os.path.isfile(src_path):
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
                    if (datar[2] == "1"): #Create directory
                        dir_path = self.__get_absolute_path(datar[3])

                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)

                        logging.info("Create directory success")
                        self.conn.send("directory|ok".encode("utf-8"));

                    if (datar[2] == "2"): #Create file
                        self.conn.send("create|ok".encode("utf-8"))
                        logging.info("Create file")
                        datarecv = ""

                        while 1:
                            data = self.conn.recv(1024)
                            datarecv += data.decode('utf-8')

                            if len(datarecv) > 0:
                                break
                        logging.info(datarecv)

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
                                t = 1024
                                if byterecv + 1024 > filesize:
                                    t = filesize - byterecv
                                buff = self.conn.recv(t)
                                if len(buff) == 0:
                                    break

                                f.write(buff)
                                byterecv += len(buff)

                            f.close()
                            logging.info("Saved file %s", file_path)

        except OSError as msg:
            logging.info(msg)
            self.conn.close()
        
        #if master disconnect then connect to slave syncs
        """
        if is__disconnect:
                time.sleep(1)
                logging.info("master disconnect then start itselt to master")
                socket_client = SocketFileClient("127.0.0.1", "6997", "master_dir")
               
                while True:
                    is_connnect = socket_client.connect()
                    logging.info(is_connnect)
                    if is_connnect == True:
                        break
                    #else:
                    #    time.sleep(1)
        """


    def senddata(self):
        return


class SocketFileServer(object):
    """
    Use as a socket client for sending data.
    """
    def __init__(self, host, port, working_dir,  socket_listener = None):
        self.host = host
        self.port = port
        self.working_dir = working_dir
        self.crypto = syncscrypto.SyncsCrypto()
        self.rsa = self.crypto.rsa_loadkey()

        if socket_listener is None:
            self.socket_listener = SocketListener()
        else:
            self.socket_listener = socket_listener

        self.thread = threading.Thread(target = self.listen)
        self.thread.start()


    def verify(self):
        sign = "DSD01|hoank|keyrc4"
        buffec = self.crypto.rsa_encrypt(sign, self.rsa)
        logging.info(buffec)
        #buffec = "%s"%buffec
        #buff = self.crypto.base64encode(buffec)
        
        buffsend = "Signature|%s"%buffec
        self.sc.send(buffsend.encode("utf-8"))
        return True

    def listen(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.soc.bind((self.host, int(self.port)))
        except socket.error as msg:
            self.soc.close()
            logging.info('Bind failed. Error Code : %s', msg)

        self.soc.listen(10)

        logging.info("listening for connections, on PORT: %s", self.port)
        is_listen = True
        while 1:
            self.sc, self.addr = self.soc.accept()
            inputready,outputready,exceptready \
                = select.select ([self.sc],[self.sc],[])
            """
            self.socket_listener.on_connect()
            logging.info("Connect by %s", self.addr)
            """
            
            #verify
            if is_listen:
              try:
                buffrecv = self.sc.recv(1024)
                buff = self.crypto.base64decode(buffrecv)
                s = buff,
            
                buff = self.crypto.rsa_decrypt(buff, self.rsa)

                buff = buff.decode("utf-8")

                check = buff.split("|")
                if check[0] != "DSD01": #check chu ky
                    self.sc.close()
                else:
                    buff += "*Master is ready"
                    logging.info(buff)
                    buffenc = self.crypto.rsa_encrypt(buff, self.rsa)
                    b64 = self.crypto.base64encode(buffenc[0])
                    self.sc.send(b64)
                    self.socket_listener.on_connect()
                    logging.info("Connect by %s", self.addr)
                    is_listen = False
              except socket.error as msg:
                self.sc.close
                self.socket_listener.on_disconnect()
                logging.info(msg)
            

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
                    time.sleep(1)
                byteSend = 0
                while 1:
                    if byteSend == filesize:
                        break
                    buff = f.read(1024)
                    self.sc.send(buff)
                    byteSend += len(buff)
            logging.info("Send file success")
        return True
       


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
        return True


    def on_modified(self, src_path, is_directory):
        if not is_directory:
            self.on_created(src_path, is_directory)        
        pass
        return True

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

        return True