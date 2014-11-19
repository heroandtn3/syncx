import sys
import time
import logging
import os
import threading
import argparse
import socket
from socket import error
 
from configobj import ConfigObj
 
import file_monitor as monitor
import ServerSyncs
 
master_cfg = {
    'host'          : '127.0.0.1',
    'port'          : '6996',
    'working_dir'   : 'master_dir',
    'is_master'    : True,
}
 
slave_cfg = {
    'host'          : '127.0.0.1',
    'port'          : '6996',
    'working_dir'   : 'slave_dir',
    'is_master'    : False,
}
 
is_RunMaster = False
 
class MyFileHandler(monitor.FileHandler):
    """Handler file changed events."""
 
    def __init__(self):
        self.is_syncs = False
 
    def set_config(self, socket_client, working_dir):
        self.socket_client = socket_client
        self.working_dir = working_dir
        self.is_syncs = False
 
 
    def set_is_syncs(self, is_syncs):
        self.is_syncs = is_syncs
        logging.info(self.is_syncs)
 
    def get_is_syncs(self):
        return self.is_syncs
 
    def __remove_working_dir(self, src_path):
        """
       Remove working directory from `src_path`.
 
       Example:
       working_dir: master_dir
           - master_dir/README.md --> README.md
           - master_dir/folder1/folder2 --> folder1/folder2.
       """
        if not src_path.startswith(self.working_dir):
            raise Exception('src_path does not contain working_dir')
        else:
            return src_path[len(self.working_dir) + 1:]
 
 
    def on_created(self, src_path, is_directory):
        super(MyFileHandler, self).on_created(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        #TODO: https://github.com/heroandtn3/syncx/issues/5
        is_syncs = self.get_is_syncs()
 
        logging.info(is_syncs)
 
        if is_syncs:
            self.socket_client.on_created(src_path, is_directory)
        else:
            #write database
            pass
 
    def on_deleted(self, src_path, is_directory):
        super(MyFileHandler, self).on_deleted(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
 
        if self.is_syncs:
            self.socket_client.on_deleted(src_path, is_directory)
        else:
            #write database
            pass
 
    def on_modified(self, src_path, is_directory):
        super(MyFileHandler, self).on_modified(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
 
        if self.is_syncs:
            self.socket_client.on_modified(src_path, is_directory)
        else:
            #write database
            pass
 
    def on_moved(self, src_path, dest_path, is_directory):
        super(MyFileHandler, self).on_moved(src_path, dest_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        dest_path = self.__remove_working_dir(dest_path)
 
        if self.is_syncs:
            self.socket_client.on_moved(src_path, dest_path, is_directory)
        else:
            #write database
            pass
 
 
handler = MyFileHandler()
 
def run_master(host, port, working_dir):
 
    logging.info('Master start')
    socket_client = ServerSyncs.SocketFileClient(host, port, working_dir)
    is_RunMaster = True
    handler.set_config(socket_client, working_dir)
    monitor.watch(working_dir, handler)
 
def run_slave(host, port, working_dir):
    logging.info('Slave start')
    socket_server = ServerSyncs.SocketFileServer(host, port, working_dir)
    if socket_server.connect():
        return True
    else:
        return False
 
def connect(host, port):
    is_connect = True
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.connect((host, int(port)))
    except socket.error as msg:
        is_connect = False
    sc.close()
 
    return is_connect
 
 
def run(config):
    config = master_cfg
    is_connect = run_slave(config['host'], config['port'], config['working_dir']) #thu connect den thang kia
    logging.info(is_connect)
 
    while True:
        """
       - if  connect success then syncs file from master to itself. Syncs success then isReady = TRUE
           if isReady:
               SEND hoi thang nao la master
               if itself is master:
                   pass
                   start_thread_master
               else:
                   top(thread slave)
                   start_thread_slave
       - else: connect fail then start_thread_master
           MASTER:
               - listen connect from client
               - sysncs file to client
               - question is_master
       """
 
        if is_connect: #connect thanh cong
            handler.set_is_syncs(True)
            #call function syncs do sang heo ro code
            #if synsc success then continue
            #config = master_cfg
            #run_slave(config['host'], config['port'], config['working_dir'])
            pass
        elif not is_RunMaster: #if connect fail then start thread master
            #master chua start
            config = master_cfg
            run_master(config['host'], config['port'], config['working_dir'])
        time.sleep(100)
 
 
if __name__ == "__main__":
 
    # config logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    run(master_cfg)