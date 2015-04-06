#-------------------------------------------------------------------------------
# regmap_analyzer.py
#
# Register map analyzer
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import pyverilog.utils.version
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import *

import pyverilog.controlflow.splitter as splitter


class CombLoopFinder(dataflow_facade):

    def search_combloop(self):

        binds = self.binds
        for tv,tk,bvi,bit,term_lsb in binds.walk_reg_each_bit():
            if 'Reg' in tv.termtype and not bvi.isCombination(): continue
            target_tree = self.makeTree(tk)
            binds.search_combloop(target_tree, bit - term_lsb, str(tk))
        return

if __name__ == '__main__':
    c_finder = CombLoopFinder("../testcode/combloop1.v")
    c_finder.search_combloop()
