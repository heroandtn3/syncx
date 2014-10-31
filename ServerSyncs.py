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
import socket
import sys
import select
import json
import logging
from configobj import ConfigObj

class ServerSync(object):

    def __init__(self):
        try:
            conf = ConfigObj("conf/serverconfig.txt")
            self.hostmaster = conf["SERVER"]["hostmater"]
            self.host = conf["SERVER"]["host"]
            self.port = conf["SERVER"]["port"]
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.soc.bind((self.hostmaster, int(self.port)))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def listen(self):
        self.soc.listen(10)


        while True:
            print "listening for connections, on PORT: ", self.port
            self.conn, self.addr = self.soc.accept()
            inputready,outputready,exceptready \
                      = select.select ([self.conn],[self.conn],[])
            data = self.conn.recv(1024)
            data = data.split("|")
            if data[0] =="syncs" and data[1] == "filename" and data[3] == "filesize":
                filename = data[2]
                filesize = int(data[4])
                self.conn.send("syncs|ok")
                f = open("E:\\" + filename, "wb")
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
                print "send file success"


        return

    def senddata(self):
        return
class SendFile(object):
    def __init_(self):
        pass
    def sendfile(self, lpFilePath):
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.connect(("127.0.0.1", 6969))
        filesize = os.path.getsize(lpFilePath)
        datasend = "syncs|filename|" + lpFilePath + "|filesize|" + str(filesize) + "|\r\n"
        print datasend
        datalen = len(datasend)
        while True:
            lSend = sc.send(datasend)
            if lSend == datalen:
                break
        datarecv = sc.recv(1024)
        print datarecv
        if datarecv == "syncs|ok":
            f = open(lpFilePath, "rb")
            byteSend = 0
            while 1:
                if byteSend == filesize:
                    break
                buff = f.read(1024)
                sc.send(buff)
                byteSend += len(buff)








