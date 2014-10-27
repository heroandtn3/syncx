#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      hoank PC
#
# Created:     27/10/2014
# Copyright:   (c) hoank PC 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class Client(object):
    def __init__(self):
        return

    def dis_connect(self):
        self.soc.close();

    def connect(self):
        conf = ConfigObj("conf/serverconfig.txt")
        self.host = conf["SERVER"]["host"]
        self.port = conf["SERVER"]["port"]
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((self.host, self.port))

    def recvdata(self):
        data = self.soc.recv(4096)
        print data

    def senddata(self, data):
        self.soc.send(data+"\n")
