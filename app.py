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
    'is_master'     : True,
}
 
slave_cfg = {
    'host'          : '127.0.0.1',
    'port'          : '6996',
    'working_dir'   : 'slave_dir',
    'is_master'     : False,
}
 
is_RunMaster = False
 
class MyFileHandler(monitor.FileHandler):
    """
    Handler file changed events.

    Params:
    - conn: a file transfer connection
    - working_dir: working directory to work on.
    """
 
    def __init__(self, conn, working_dir):
        self.conn = conn
        self.working_dir = working_dir
 
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
        if self.conn.on_created(src_path, is_directory):
            logging.info('Create successful')
        else:
            logging.info('Opps')

    def on_deleted(self, src_path, is_directory):
        super(MyFileHandler, self).on_deleted(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        self.conn.on_deleted(src_path, is_directory)

    def on_modified(self, src_path, is_directory):
        super(MyFileHandler, self).on_modified(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        self.conn.on_modified(src_path, is_directory)

    def on_moved(self, src_path, dest_path, is_directory):
        super(MyFileHandler, self).on_moved(src_path, dest_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        dest_path = self.__remove_working_dir(dest_path)
        self.conn.on_moved(src_path, dest_path, is_directory)
 
 
def try_connect(host, port):
    """
    Check if is there any running server (a app instance) that may be master.

    Return that socket if connection is availabe, else return None.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))
    except OSError as err:
        logging.debug('No connection established, OSError: %s', err)
        return None

    return sock
 
 
def run_master(host, port, working_dir):
    logging.info('Master start')
    socket_client = ServerSyncs.SocketFileServer(host, port, working_dir)
    handler = MyFileHandler(socket_client, working_dir)
    monitor.watch(working_dir, handler)

def run_slave(host, port, working_dir):
    logging.info('Slave start')
    socket_server = ServerSyncs.SocketFileClient(host, port, working_dir)
    socket_server.connect()

def run(config):
    target = run_master if config['is_master'] else run_slave
    try:
        thread = threading.Thread(
            target=target,
            args=(config['host'], config['port'], config['working_dir']))
        thread.start()
    except:
        logging.error('Error when running thread')
 
if __name__ == "__main__":
 
    # config logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    sock = try_connect(master_cfg['host'], master_cfg['port'])
    if sock:
        # oh, that may be a master, I must be slave now
        sock.close() # TODO: reuse this socket
        run(slave_cfg)
    else:
        # opps, I'm gonna be master now
        run(master_cfg)
