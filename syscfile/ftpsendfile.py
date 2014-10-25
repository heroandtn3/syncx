#-------------------------------------------------------------------------------
# Name:        File transfer among FTP servers
# Purpose:
#
# Author:      Administrator PC
#
# Created:     25/10/2014
# Copyright:   (c) Administrator PC 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import logging
import logging.config
import threading

from configobj import ConfigObj
from ftplib     #socket-based ftp 

class SendFile(threading.Thread):
    def __init__(self):
        self.status = False

    def connect(self):
        """
        user information store config file
        """
        conf = ConfigObj("conf/ftpconfig.txt")
        self.ftpserver = conf["ftpserver"]["ftpserver"]
        self.ftpuser = conf["ftpserver"]["ftpuser"]
        self.ftppass = conf["ftpserver"]["ftppass"]
        self.ftp = ftplib.FTP(ftpserver, ftpuser, ftppass)
        self.user = (ftpserver, ftppass)
        ftp.login(user)

    def dis_connect():
        self.ftp.quit()
        

    def start_sendfile_to_other(file,dir):
        """
         Send file to another FTP server
         @para: 
            file: file to send
            dir: dir store this file in locate destination
        """
        self.connect()
        self.ftp.cwd()
        localdata = open(file, "rb")
        self.ftp.storbinary('STOR', file, localdata, 1024)
        localdata.close()
        print "Done"
        dis_connect()


    
        


