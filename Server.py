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


class Server(object):
    def __init__(self):
        return

    def dis_connect(self):
        self.soc.close();

    def start(self):
        conf = ConfigObj("conf/serverconfig.txt")
        self.host = conf["SERVER"]["host"]
        self.port = conf["SERVER"]["port"]
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.soc.bind((self.host, self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        self.soc.listen(10)
        while 1:
            conn, addr = self.soc.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])

        self.dis_connect()
    def recvdata(self):
        data = self.soc.recv(4096)
        print data

    def senddata(self):
        self.soc.send("hoank\n")

