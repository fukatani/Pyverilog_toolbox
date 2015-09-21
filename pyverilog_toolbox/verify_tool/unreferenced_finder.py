#-------------------------------------------------------------------------------
# unreferenced_finder.py
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
from pyverilog_toolbox.verify_tool.bindlibrary import eval_value

class UnreferencedFinder(dataflow_facade):

    def decorate_html(html_name):
        temp_html = open('temp.html', 'r')
        out_html = open(html_name, 'w')
        for line in temp_html:
            out_html.write(line + '<br>')
        temp_html.close()
        out_html.close()

    @out_as_html(decorate_html)
    def search_unreferenced(self):
        """[FUNCTIONS]
        search input/reg/wire which not referenced any other output/reg/wire.
        """
        signals = []
        for tv, tk in self.binds.walk_signal():
            #Exclude parameter and function.
            if not set(['Input', 'Reg', 'Wire']) & tv.termtype: continue
            if 'Output' in tv.termtype: continue #because referenced as output.
            signals.append(str(tk))

        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            target_tree = self.makeTree(tk)
            trees = self.binds.extract_all_dfxxx(target_tree, set([]), bit - tv.lsb.eval(), DFTerminal)
            trees.add((bvi.getClockName(), bvi.getClockBit()))
            trees.add((bvi.getResetName(), bvi.getResetBit()))
            for tree, bit in trees:
                if str(tree) in signals:
                    signals.remove(str(tree))
        if signals:
            print("finded unreferenced variables: " + str(signals))
        else:
            print("There isn't unreferenced variables.")
        return signals

    @out_as_html(decorate_html)
    def search_floating(self):
        floating_signals = []
        for tv, tk in self.binds.walk_signal():
            if not set(['Reg', 'Wire']) & tv.termtype: continue
            if not tk in self.binddict.keys():
                floating_signals.append(str(tk))
            else:
                term_bits = set([i for i in range(eval_value(tv.lsb), eval_value(tv.msb) + 1)])
                for bind in self.binddict[tk]:
                    bind_bits = set([ i for i in range(eval_value(bind.lsb), eval_value(bind.msb) + 1)])
                    term_bits = term_bits - (term_bits & bind_bits) #delete if binded
                if not term_bits: continue
                for float_bit in term_bits:
                    floating_signals.append(str(tk) + '[' + str(float_bit) + ']')

        if floating_signals:
            print("floating nodes: " + str(floating_signals))
        else:
            print("There isn't floating nodes.")
        return floating_signals

if __name__ == '__main__':
    u_finder = UnreferencedFinder("../testcode/floating.v")
    u_finder.search_unreferenced()
    u_finder.search_floating()
