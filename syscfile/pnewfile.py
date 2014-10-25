import os

class CNewFile(object):
    def __init__(self):
        self.filepath = ""
        self.directory = ""

    def newfile(self, filepath, directory):
        s = "Create file" + filepath + " " + directory
        print s
        return

    def deletefile(self, filepath, directory):
        return

    def modifiedfile(self, filepath, directory):
        return

    def movedfile(self, filepath, directory):
        return