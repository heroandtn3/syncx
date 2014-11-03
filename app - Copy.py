import sys
import time
import logging
import threading
import file_monitor as monitor
from syscfile import pnewfile
import ServerSyncs
from configobj import ConfigObj

server = ServerSyncs.ServerSync()
sfile = pnewfile.CNewFile()

class MyFileHandler(monitor.FileHandler):
    """
    Cac event se duoc goi, Hoa va Duy su dung cac event nay de thuc hien
    truyen file,... bla bla.
    """

    def on_created(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On created: %s', src_path)
        print (src_path)
        sfile.new_file(src_path, is_directory)

    def on_deleted(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On deleted: %s', src_path)
        sfile.delete_file(src_path, is_directory)


    def on_modified(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On modified: %s', src_path)
        """
        if file modifed then
            cach 1: extent created new file
            cach 2: thuc hien sau
        """
        sfile.new_file(src_path, is_directory)


    def on_moved(self, src_path, dest_path, is_directory):
        # TODO: implement this
        logging.info('On moved: %s to %s', src_path, dest_path)
        #send move file client to server
        sfile.moved_file(src_path, is_directory)

def monitor_fun(path):
    logging.info("Monitor start")
    handler = MyFileHandler()
    monitor.watch(path, handler)

if __name__ == "__main__":

    # config logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    #get folder
    conf = ConfigObj("conf/folderconfig.txt")
    folderserver1 = conf["FOLDER"]["server1"]
    folderserver2 = conf["FOLDER"]["server2"]

    # start watch file changing


    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    path = folderserver2

    try:
        t1 = threading.Thread(target = server.listen, args = (path, ))
        #t2 = threading.Thread(target = monitor_fun, args = (path,))
        t1.start()
        #t2.start()
    except:
        logging.info("thread monito file")

    #handler.on_created("requirements.txt", "E:\\")