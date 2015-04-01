#-------------------------------------------------------------------------------
# test_ra.py
#
#
#
# Copyright (C) 2015, ryosuke fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------


import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from pyverilog_toolbox.verify_tool.ra_interface import *
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal(self):
        write_map, read_map = analize_regmap('regmap.v', 'setup.txt')
        self.assertEqual(str(write_map.map), "{0: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1)}, 1: {0: ('TOP.reg1', 0)}}")
        self.assertEqual(str(read_map.map), "{0: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1)}, 1: {0: ('TOP.reg1', 0)}}")
    def test_split(self):
        write_map, read_map = analize_regmap('regmap_split.v', 'setup.txt')
        self.assertEqual(str(write_map.map),
                        "{1: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1), 2: ('TOP.reg1', 2), 3: ('TOP.reg1', 3)}}")
        self.assertEqual(str(read_map.map),
                        "{1: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1), 2: ('TOP.reg1', 2), 3: ('TOP.reg1', 3)}}")

if __name__ == '__main__':
    unittest.main()
