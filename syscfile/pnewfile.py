import os
import ServerSyncs
server = ServerSyncs.SendFile()
class CNewFile(object):
    def __init__(self):
        self.filepath = ""
        self.directory = ""

    def newfile(self, filepath, directory):
        s = "Create file" + filepath + " " + directory
        print s
        server.sendfile(filepath)

    def deletefile(self, filepath, directory):
        #delete file
        sFile.deleteFile(filepath)

    def modifiedfile(self, filepath, directory):
        #modified file
        return

    def movedfile(self, filepath, dest_path, directory):
        #moved file

        return