import sys
import time
import logging
import file_monitor as monitor
from syscfile import pnewfile
import ServerSyncs

sfile = pnewfile.CNewFile()

class MyFileHandler(monitor.FileHandler):
    """
    Cac event se duoc goi, Hoa va Duy su dung cac event nay de thuc hien
    truyen file,... bla bla.
    """

    def on_created(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On created: %s', src_path)
        sfile.newfile(src_path, is_directory)

    def on_deleted(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On deleted: %s', src_path)
        sfile.deletefile(src_path, is_directory)


    def on_modified(self, src_path, is_directory):
        # TODO: implement this
        logging.info('On modified: %s', src_path)
        """
        if file modifed then
            cach 1: extent created new file
            cach 2: thuc hien sau
        """
        sfile.newfile(src_path, is_directory)


    def on_moved(self, src_path, dest_path, is_directory):
        # TODO: implement this
        logging.info('On moved: %s to %s', src_path, dest_path)
        #send move file client to server
        sfile.movedfile(src_path, is_directory)



if __name__ == "__main__":

    # config logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # start watch file changing
    #path = sys.argv[1] if len(sys.argv) > 1 else '.'
    handler = MyFileHandler()
    #monitor.watch(path, handler)
    #server.listen()
    handler.on_created("NET - 1.pdf", "E:\\")