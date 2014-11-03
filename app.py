import sys
import time
import logging
import threading
import argparse

from configobj import ConfigObj

import file_monitor as monitor
import ServerSyncs

master_cfg = {
    'host'          : '127.0.0.1',
    'port'          : '6969',
    'working_dir'   : 'master_dir',
    'is_master'    : True,
}

slave_cfg = {
    'host'          : '127.0.0.1',
    'port'          : '6969',
    'working_dir'   : 'slave_dir',
    'is_master'    : False,
}

class MyFileHandler(monitor.FileHandler):
    """Handler file changed events."""

    def __init__(self, socket_client, working_dir):
        self.socket_client = socket_client
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
        self.socket_client.on_created(src_path, is_directory)

    def on_deleted(self, src_path, is_directory):
        super(MyFileHandler, self).on_deleted(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        self.socket_client.on_deleted(src_path, is_directory)

    def on_modified(self, src_path, is_directory):
        super(MyFileHandler, self).on_modified(src_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        self.socket_client.on_modified(src_path, is_directory)

    def on_moved(self, src_path, dest_path, is_directory):
        super(MyFileHandler, self).on_moved(src_path, dest_path, is_directory)
        src_path = self.__remove_working_dir(src_path)
        self.socket_client.on_moved(src_path, dest_path, is_directory)


def run_master(host, port, working_dir):
    logging.info('Master start')
    socket_client = ServerSyncs.SocketFileClient(host, port, working_dir)
    handler = MyFileHandler(socket_client, working_dir)
    monitor.watch(working_dir, handler)

def run_slave(host, port, working_dir):
    logging.info('Slave start')
    socket_server = ServerSyncs.SocketFileServer(host, port, working_dir)
    socket_server.listen()

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
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # config args
    parser = argparse.ArgumentParser(description='Synx tool')
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