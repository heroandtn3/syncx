import sys
import time
import logging
import os
import threading
import argparse
import socket
import hashlib
from socket import error
from time import gmtime, strftime

from configobj import ConfigObj

import file_monitor as monitor
import ServerSyncs
import syncscrypto
import utils
import statusserver

master_cfg = {
    'host'          : '127.0.0.1',
    'port'          : 6996,
    'working_dir'   : 'master_dir',
    'is_master'     : True,
    'redis_host'    : '127.0.0.1',
    'redis_port'    : 2013,
    'status_host'   : '127.0.0.1',
    'status_port'   : 1991,
}

slave_cfg = {
    'host'          : '127.0.0.1',
    'port'          : 6996,
    'working_dir'   : 'slave_dir',
    'is_master'     : False,
    'redis_host'    : '127.0.0.1',
    'redis_port'    : 2014,
    'status_host'   : '127.0.0.1',
    'status_port'   : 1992,

}

is_RunMaster = False

class MyFileHandler(monitor.FileHandler):
    """
    Handler file changed events.

    Params:
    - conn: a file transfer connection
    - working_dir: working directory to work on.
    """

    def __init__(self, host, port, working_dir, conn, sync_logger):
        self.working_dir = working_dir
        self.conn = conn
        self.sync_logger = sync_logger
        self.connected = False

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
        
    def dispatch(self, data):
        _data = data.decode().split(':')
        operator = _data[0]
        if operator == 'mov':
            src_path = _data[1]
            dest_path = _data[2]
            is_directory = _data[3] == 'd'
        else:
            src_path = _data[1]
            is_directory = _data[2] == 'd'
        sync_success = False
        if operator == 'cre':
            sync_success = self.on_created(src_path, is_directory)
        elif operator == 'del':
            sync_success = self.on_deleted(src_path, is_directory)
        elif operator == 'mod':
            sync_success = self.on_modified(src_path, is_directory)
        elif operator == 'mov':
            sync_success = self.on_moved(src_path, dest_path, is_directory)
        if sync_success:
            self.sync_logger.del_not_sync(data)


    def on_created(self, src_path, is_directory):
        super(MyFileHandler, self).on_created(src_path, is_directory)
        #TODO: https://github.com/heroandtn3/syncx/issues/5
        if self.connected:
            _src_path = self.__remove_working_dir(src_path)
            if self.conn.on_created(_src_path, is_directory):
                self.sync_logger.save_last_sync()
                return True
        self.sync_logger.save_not_sync(
                'cre:%s:%s' % (src_path, 'd' if is_directory else 'f'),
                time.time())
        return False

    def on_deleted(self, src_path, is_directory):
        super(MyFileHandler, self).on_deleted(src_path, is_directory)

        if self.connected:
            _src_path = self.__remove_working_dir(src_path)
            if self.conn.on_deleted(_src_path, is_directory):
                self.sync_logger.save_last_sync()
                return True
        self.sync_logger.save_not_sync(
                'del:%s:%s' % (src_path, 'd' if is_directory else 'f'),
                time.time())
        return False

    def on_modified(self, src_path, is_directory):
        super(MyFileHandler, self).on_modified(src_path, is_directory)

        if self.connected:
            _src_path = self.__remove_working_dir(src_path)
            if self.conn.on_modified(_src_path, is_directory):
                self.sync_logger.save_last_sync()
                return True
        self.sync_logger.save_not_sync(
                'mod:%s:%s' % (src_path, 'd' if is_directory else 'f'),
                time.time())
        return False

    def on_moved(self, src_path, dest_path, is_directory):
        super(MyFileHandler, self).on_moved(src_path, dest_path, is_directory)
        
        if self.connected:
            _src_path = self.__remove_working_dir(src_path)
            _dest_path = self.__remove_working_dir(dest_path)
            if self.conn.on_moved(_src_path, _dest_path, is_directory):
                self.sync_logger.save_last_sync()
                return True
        self.sync_logger.save_not_sync(
                'mov:%s:%s:%s' % (src_path, dest_path,
                                  'd' if is_directory else 'f'),
                time.time())
        return False

def try_connect(host, port):
    """
    Check if is there any running server (a app instance) that may be master.

    Return that socket if connection is availabe, else return None.
    """
    is_connect = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))


        crypto = syncscrypto.SyncsCrypto()
        rsa = crypto.rsa_loadkey()
        strtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        signature = "Ping|DSD01|" + str(strtime)
        logging.info("signature is: %s" %signature)
        buffenc = crypto.rsa_encrypt(signature, rsa)
        b64 = crypto.base64encode(buffenc[0])
        sock.send(b64)

        buffrecv = sock.recv(1024)
        buff = crypto.base64decode(buffrecv)
        s = buff,

        buff = crypto.rsa_decrypt(buff, rsa)
        buff = buff.decode("utf-8")
        logging.info(buff)

        check = buff.split("*")
        if check[0] == signature and check[1] == "Master is ready": #check chu ky
            is_connect = True
    except OSError as err:
        logging.debug('No connection established, OSError: %s', err)
        return None

    sock.close()
    return is_connect

class App():

    def __init__(self, config=master_cfg):
        self.config = config
        self.host = config['host']
        self.port = config['port']
        self.working_dir = config['working_dir']
        self.is_master = config['is_master']
        self.redis_host = config['redis_host']
        self.redis_port = config['redis_port']
        self.status_host = config['status_host']
        self.status_port = config['status_port']
        
        self.sync_logger = utils.RedisSyncLogger(
            host=self.redis_host,
            port=self.redis_port)
        self.is_run_as_master = False
        self.name = 'MASTER' if self.is_master else 'SLAVE'
        self.status_server = statusserver.HttpStatusServer(
            port=self.status_port)
        self.status_server.start()


    def start(self):
        logging.info('%s starts...', self.name)

        is_connect = try_connect(master_cfg['host'], master_cfg['port'])
        if is_connect:
            self.run_as_slave()
        else:
            self.run_as_master()

    def run_as_master(self):
        self.is_run_as_master = True
        logging.info('%s is running as master', self.name)
        conn = ServerSyncs.SocketFileServer(
            self.host, self.port, self.working_dir,
            socket_status_callback=self.socket_status_callback)
        self.handler = MyFileHandler(
            self.host, self.port, 
            self.working_dir, conn, self.sync_logger)
        monitor.watch(self.working_dir, self.handler)
        self.status_server.set_ready(True)

    def run_as_slave(self):
        self.is_run_as_master = False
        logging.info('%s is running as slave', self.name)
        conn = ServerSyncs.SocketFileClient(
            self.host, self.port, self.working_dir,
            socket_status_callback=self.socket_status_callback)
        conn.connect()
        self.status_server.set_ready(False)

    def socket_status_callback(self, is_connect):
        if is_connect:
            self.__on_connect()
        else:
            self.__on_disconnect()

    def __on_connect(self):
        need_convert = False
        if self.is_run_as_master:
            if not self.is_master:
                logging.info('Connect to temporary slave successful!')
                # I'm just temporary master, I should promote current slave
                # to master
                need_convert = True
            else:
                logging.info('Connect to permanent slave successful!')
            
            # start sync
            self.handler.connected = True

            # detect file changes from last_sync timestamp
            last_sync = self.sync_logger.get_last_sync()
            logging.debug('Last time sync: %s', last_sync)
            if last_sync:
                # last_sync available
                # start scan file change from last_sync
                for data in self.sync_logger.get_not_sync_list():
                    self.handler.dispatch(data)

            else:
                logging.debug('First time start app')
                # scan all file
                for src_path, is_directory in utils.scan_dir(self.working_dir):
                    self.handler.on_created(src_path, is_directory)
            self.sync_logger.save_last_sync()
            
            if need_convert:
                self.convert()

        else:
            if self.is_master:
                logging.info('Connect to temporary master successful!')
                # should be converted to master when finish sync-ing
            else:
                logging.info('Connect to permanent master successful!')

    def __on_disconnect(self):
        if self.is_run_as_master:
            handler.connected = False
        else:
            # hmm, master is died, what can I do now :(
            # so, start as master now :)
            self.run_as_master()

    def convert(self):
        """
        Convert between master and slave.
        """
        pass

def run(config):
    app = App(config)
    try:
        thread = threading.Thread(
            target=app.start)
        thread.start()
    except:
        logging.error('Error when running thread')


# =========================== MAIN APP ==================================== #

if __name__ == "__main__":

    # config logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # config args
    parser = argparse.ArgumentParser(description='Syncx tool')
    parser.add_argument(
        '-m', '--master',
        default=False,
        action='store_true',
        help=('Run app as master')
    )
    args = parser.parse_args()

    # Note: run slave first before run master
    if args.master:
        run(master_cfg)
    else:
        run(slave_cfg)
