import unittest
from test import support
import os

import utils

class TestUtils(unittest.TestCase):

    def setUp(self):
        """code to execute in preparation for tests."""
        pass

    def tearDown(self):
        """code to execute to clean up after tests"""
        pass

    def test_scan_dir(self):
        dirname = 'conf'
        list_files = ['folderconfig.txt', 'ftpconfig.txt', 'serverconfig.txt']
        files = [f for f in utils.scan_dir('conf')]
        self.assertEqual(files, [os.path.join(dirname, f) for f in list_files])

if __name__ == '__main__':
    unittest.main()