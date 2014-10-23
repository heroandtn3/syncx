from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
import logging

class FileHandler():
    """
    Handler to use when monitor a directory.
    """

    def on_created(self, src_path, is_directory):
        logging.info('On created: %s', src_path)

    def on_deleted(self, src_path, is_directory):
        logging.info('On deleted: %s', src_path)

    def on_modified(self, src_path, is_directory):
        logging.info('On modified: %s', src_path)

    def on_moved(self, src_path, dest_path, is_directory):
        logging.info('On moved: %s to %s', src_path, dest_path)


class XFileSystemEventHandler(FileSystemEventHandler):
    """
    Custom FileSystemEvent class.
    """

    def __init__(self, file_handler):
        super(XFileSystemEventHandler, self).__init__()
        self.handler = file_handler

    def on_created(self, event):
        self.handler.on_created(event.src_path, event.is_directory)

    def on_deleted(self, event):
        self.handler.on_deleted(event.src_path, event.is_directory)

    def on_modified(self, event):
        self.handler.on_modified(event.src_path, event.is_directory)

    def on_moved(self, event):
        self.handler.on_moved(event.src_path, event.dest_path, 
                              event.is_directory)


def watch(src_path, file_handler):
    """
    Watch file changing in a directory.

    src_path: path to directory to be monitored.
    file_handler: handler to be invoked.
    """
    event_handler = XFileSystemEventHandler(file_handler)
    observer = Observer()
    observer.schedule(event_handler, src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except:
        observer.stop()
        logging.info('Monitor exits!')
    observer.join()