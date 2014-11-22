import os
import logging

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
        for f in filenames:
            yield os.path.join(dirpath, f)

class RedisSyncLogger():

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_last_sync(self):
        try:
            return self.r.get('last_sync')
        except redis.exceptions.ConnectionError as err:
            logging.debug('Redis connection error: %s', err)
            return None

    def save_not_sync(self, member, score):
        try:
            return self.r.zadd('notsync', member, score)
        except redis.exceptions.ConnectionError as err:
            logging.debug('Redis connection error: %s', err)
            return None

if __name__ == '__main__':
    for f in scan_dir('conf'):
        print(f)
