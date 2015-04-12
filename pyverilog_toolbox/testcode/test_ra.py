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
from pyverilog_toolbox.verify_tool.combloop_finder import *
from pyverilog_toolbox.verify_tool.bindlibrary import *
from pyverilog_toolbox.verify_tool.cnt_analyzer import *
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_cnt_analyzer(self):
        c_analyzer = CntAnalyzer("norm_cnt2.v")
        cnt_dict = c_analyzer.analyze_cnt()
        self.assertEqual(cnt_dict['TOP.down_cnt'].tostr(),
                        "name: TOP.down_cnt\ncategory: down counter\nreset val: 0" +
                        "\nmax_val: 4\nmother counter:set([])")
        self.assertEqual(cnt_dict['TOP.up_cnt'].tostr(),
                        'name: TOP.up_cnt\ncategory: up counter\nreset val: 0' +
                        '\nmax_val: 6\nmother counter:set([])')
        self.assertEqual(cnt_dict['TOP.up_cnt2'].tostr(),
                        "name: TOP.up_cnt2\ncategory: up counter\nreset val: 0" +
                        "\nmax_val: 4\nmother counter:set(['TOP.up_cnt'])")
        c_analyzer.make_cnt_event_all()
        self.assertEqual(str(c_analyzer.cnt_dict['TOP.up_cnt'].cnt_event_dict),
                        '{2: ["TOP.now=\'d1 @(TOP_up_cnt==3\'d2)", "TOP.is_count_max=\'d1 @(TOP_up_cnt==3\'d2)", "TOP.up_cnt2=\'d0 @(TOP_up_cnt==3\'d2)"]}')

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

    def test_comb_loop(self):
        c_finder = CombLoopFinder("combloop.v")
        with self.assertRaises(CombLoopException):
            c_finder.search_combloop()
        c_finder = CombLoopFinder("not_combloop.v")
        c_finder.search_combloop()

    def test_comb_loop1(self):
        c_finder = CombLoopFinder("combloop1.v")
        with self.assertRaises(CombLoopException):
            c_finder.search_combloop()

    def test_comb_loop2(self):
        c_finder = CombLoopFinder("combloop2.v")
        with self.assertRaises(CombLoopException):
            c_finder.search_combloop()


if __name__ == '__main__':
    unittest.main()
