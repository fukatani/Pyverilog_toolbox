#-------------------------------------------------------------------------------
# unreferenced_finder.py
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os
import copy
import collections

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import pyverilog.utils.version
from pyverilog.utils.util import *
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import *
from pyverilog_toolbox.verify_tool.bindlibrary import *

import pyverilog.controlflow.splitter as splitter


class UnreferencedFinder(dataflow_facade):

    def search_unreferenced(self):
        """[FUNCTIONS]
        search input/reg/wire which not referenced any other output/reg/wire.
        """
        signals = []
        for tv,tk in self.binds.walk_signal():
            if not set(['Input', 'Reg', 'Wire']) & tv.termtype: continue
            if 'Output' in tv.termtype: continue
            signals.append(str(tk))

        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            target_tree = self.makeTree(tk)
            trees = self.binds.extract_all_dfxxx(target_tree, set([]), bit, pyverilog.dataflow.dataflow.DFTerminal)
            trees.add((bvi.getClockName(), bvi.getClockBit()))
            trees.add((bvi.getResetName(), bvi.getResetBit()))
            for tree, bit in trees:
                if str(tree) in signals:
                    signals.remove(str(tree))
        print "finded unreferenced variables: " + str(signals)
        return signals

if __name__ == '__main__':
    u_finder = UnreferencedFinder("../testcode/unreferenced_variables.v")
    u_finder.search_unreferenced()
