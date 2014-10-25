#-------------------------------------------------------------------------------
# Name:        module1
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

from configobj import ConfigObj
from ftplib import FTP

class SendFile(object):
    def __init__(self):
        self.status = False

    def connect(self):
        conf = ConfigObj("conf/ftpconfig.txt")
        ftpserver = conf["ftpserver"]["ftpserver"]
        ftpuser = conf["ftpserver"]["ftpuser"]
        ftppass = conf["ftpserver"]["ftppass"]
        ftp = FTP(ftpserver, ftpuser, ftppass)
        ftp.login(ftpserver, ftppass)
        filename = "conf/ftpconfig.txt"
        ftp.storbinary('STOR %s' % filename, open(filename, 'w').write)


