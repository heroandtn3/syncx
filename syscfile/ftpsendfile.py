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
import ftplib     #socket-based ftp

class SendFile(threading.Thread):
    def __init__(self):
        self.status = False

    def connect(self):
        """
        user information store config file
        """
        try:
            conf = ConfigObj("conf/ftpconfig.txt")
            self.ftpserver = conf["ftpserver"]["ftpserver"]
            self.ftpuser = conf["ftpserver"]["ftpuser"]
            self.ftppass = conf["ftpserver"]["ftppass"]
            self.ftp = ftplib.FTP(self.ftpserver)
            self.ftp.login(self.ftpuser, self.ftppass)
        except ftplib.error_perm, resp:
            print resp

    def dis_connect(self):
        self.ftp.quit()

    def deleteFile(self, file, dir):
        self.connect()
        self.ftp.delete(file)

    def start_sendfile_to_other(self, file, dir):
        """
         Send file to another FTP server
         @para:
            file: file to send
            dir: dir store this file in locate destination
        """
        self.connect()
       # self.ftp.cwd()

        localdata = open(file, "rb")
        self.ftp.mkd("/hoank2")
        self.ftp.storbinary('STOR /hoank2/'+ file, localdata, 1024)
        localdata.close()
        print "Done. Store in: ",dir
        #self.dis_connect();






