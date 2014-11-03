import os
import ServerSyncs
server = ServerSyncs.SendFile()
class CNewFile(object):
    def __init__(self):
        self.filepath = ""
        self.directory = ""

    def new_file(self, filepath, directory):
        server.sendfile(filepath)

    def delete_file(self, filepath, directory):
        #delete file
        sFile.deleteFile(filepath)

    def modified_file(self, filepath, directory):
        #modified file
        return

    def moved_file(self, filepath, dest_path, directory):
        #moved file

        return