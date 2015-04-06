#-------------------------------------------------------------------------------
# test_ra.py
#
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------


import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from pyverilog_toolbox.verify_tool.regmap_analyzer import *
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal(self):
        ranalyzer = RegMapAnalyzer("regmap.v", "setup.txt")
        write_map, read_map = ranalyzer.getRegMaps()
        self.assertEqual(str(write_map.map), "{0: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1)}, 1: {0: ('TOP.reg1', 0)}}")
        self.assertEqual(str(read_map.map), "{0: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1)}, 1: {0: ('TOP.reg1', 0)}}")
    def test_split(self):
        ranalyzer = RegMapAnalyzer("regmap_split.v", "setup.txt")
        write_map, read_map = ranalyzer.getRegMaps()
        self.assertEqual(str(write_map.map),
                        "{1: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1), 2: ('TOP.reg1', 0), 3: ('TOP.reg1', 1)}}")
        self.assertEqual(str(read_map.map),
                        "{1: {0: ('TOP.reg0', 0), 1: ('TOP.reg0', 1), 2: ('TOP.reg1', 0), 3: ('TOP.reg1', 1)}}")
    def test_partselect(self):
        df = dataflow_facade("complex_partselect.v")
        self.assertEqual(df.print_bind_info(),
                        'TOP.reg0[3]: set([(TOP.reg0, 3), (TOP.WRITE, 0), (TOP.WRITE_DATA, 1)])' +
                        'TOP.reg0[4]: set([(TOP.reg0, 4), (TOP.WRITE_DATA, 2), (TOP.WRITE, 0)])')

    def test_split2(self):
        ranalyzer = RegMapAnalyzer("regmap2.v", "setup.txt")
        write_map, read_map = ranalyzer.getRegMaps()
        self.assertEqual(str(write_map.map),
                        "{0: {0: ('TOP.reg0', 3), 1: ('TOP.reg0', 4)}}")
        self.assertEqual(str(read_map.map),
                        "{0: {0: ('TOP.reg0', 3), 1: ('TOP.reg0', 4)}}")
if __name__ == '__main__':
    unittest.main()
