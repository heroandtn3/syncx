import os
import logging
import time

# 3-party modules
import redis

def scan_dir(src_path):
    """
    Scan for files in `src_path` directory

    Return a generator of file paths.
    """
    if not os.path.isdir(src_path):
        raise Exception('src_path does not contain working_dir')
    for dirpath, dirnames, filenames in os.walk(src_path):
        for d in dirnames:
            yield os.path.join(dirpath, d), True
        for f in filenames:
            yield os.path.join(dirpath, f), False


class RedisSyncLogger():

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def get_last_sync(self):
        try:
            return self.r.get('last_sync')
        except redis.exceptions.ConnectionError as err:
            logging.debug('Redis connection error: %s', err)
            return None

    def save_last_sync(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.r.set('last_sync', timestamp)

    def save_not_sync(self, member, score):
        try:
            return self.r.zadd('notsync', score, member)
        except redis.exceptions.ConnectionError as err:
            logging.debug('Redis connection error: %s', err)
            return None

    def get_not_sync_list(self):
        for member, score in self.r.zscan_iter('notsync'):
            yield member

    def del_not_sync(self, member):
        try:
            return self.r.zrem('notsync', member)
        except redis.exceptions.ConnectionError as err:
            logging.debug('Redis connection error: %s', err)
            return None

if __name__ == '__main__':
    for f in scan_dir('conf'):
        print(f)
