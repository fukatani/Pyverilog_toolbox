#-------------------------------------------------------------------------------
# codeclone_finder.py
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
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import *
from pyverilog_toolbox.verify_tool.bindlibrary import *

import pyverilog.controlflow.splitter as splitter


class CodeCloneFinder(dataflow_facade):

    def search_regclone(self):
        """[FUNCTIONS]
        search register pairs that always hold same values.

        ex.
        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg2 <= 1'b0;
            end else begin
                reg2 <= 1'b1;
            end
        end

        assign in1 = IN;

        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg3 <= 1'b0;
            end else begin
                reg3 <= in1;
            end
        end
        """
        code_dict = {}
        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            if not 'Reg' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            code_dict[tk, bit] = target_tree.tocode()

        #sort for assign code(same assign reg must line up next to)
        cd_order = collections.OrderedDict(sorted(code_dict.items(), key=lambda t: t[1]))
        ##print cd_order
        clone_regs = []
        for cnt in range(len(cd_order.keys()) - 1):
            if cd_order.values()[cnt] == cd_order.values()[cnt + 1]:
                clone_regs.append((cd_order.keys()[cnt], cd_order.keys()[cnt + 1]))
        return clone_regs

    def search_invert_regs(self):
        def judge_invert_reg(values, target_values):
            assert len(values) == len(target_values)
            for val, target_val in zip(values, target_values):
                pass

            return True

        functable = {}
        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            if not 'Reg' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            functable[tk, bit] = splitter.split(target_tree)

        ft_order = collections.OrderedDict(sorted(functable.items(), key=lambda t: t[0]))
        print ft_order

        for cnt in range(len(ft_order.keys()) - 1):
            for target_cnt in range(cnt + 1, len(ft_order.keys())):
                if ft_order.values()[cnt].keys() == ft_order.values()[target_cnt].keys():#same branch or not
                    judge_invert_reg(ft_order.values()[cnt].values(), ft_order.values()[target_cnt].values())
                else:
                    break

if __name__ == '__main__':
    codeclone_finder = CodeCloneFinder("../testcode/reg_clone.v")
    #codeclone_finder.search_invert_regs()
    print(str(codeclone_finder.search_regclone()))


