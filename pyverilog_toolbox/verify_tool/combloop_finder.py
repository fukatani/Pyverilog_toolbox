#-------------------------------------------------------------------------------
# combloop_finder.py
#
# finding combinational loop in RTL design.
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import dataflow_facade, out_as_html


class CombLoopFinder(dataflow_facade):

    def decorate_html(html_name):
        temp_html = open('temp.html', 'r')
        out_html = open(html_name, 'w')
        for line in temp_html:
            out_html.write(line + '<br>')
        temp_html.close()
        out_html.close()

    @out_as_html(decorate_html)
    def search_combloop(self):
        binds = self.binds
        for tv, tk, bvi, bit, term_lsb in binds.walk_reg_each_bit():
            if 'Reg' in tv.termtype and not bvi.isCombination(): continue
            target_tree = self.makeTree(tk)
            binds.search_combloop(target_tree, bit - term_lsb, str(tk), bit - term_lsb)
        print('There is no combinational loop.')

if __name__ == '__main__':
    c_finder = CombLoopFinder("../testcode/not_combloop.v")
    c_finder.search_combloop()

