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
                reg2 <= IN;
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
        clone_regs = []
        for cnt in range(len(cd_order.keys()) - 1):
            if cd_order.values()[cnt] == cd_order.values()[cnt + 1]:
                clone_regs.append((cd_order.keys()[cnt], cd_order.keys()[cnt + 1]))

        if clone_regs:
            print('Clone reg pairs: '+ str(clone_regs))
        else:
            print('There isn\'t clone reg pair.')
        return clone_regs

    def search_invert_regs(self):
        """[FUNCTIONS]
        search register pairs that always hold invert values.

        ex.
        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg1 <= 1'b0;
            end else begin
                reg1 <= IN;
            end
        end

        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg2 <= 1'b1;
            end else begin
                reg2 <= !IN;
            end
        end
        """
        def judge_invert_reg(values, target_values):
            assert len(values) == len(target_values)
            for val, target_val in zip(values, target_values):
                if isinstance(val, pyverilog.dataflow.dataflow.DFEvalValue) and isinstance(target_val, pyverilog.dataflow.dataflow.DFEvalValue):
                    if eval_value(val) == eval_value(target_val):
                        return False
                elif str(val) == 'Ulnot':
                    if val.nextnodes[0].tocode() != target_val.tocode():
                        return False
                elif str(target_val) == 'Ulnot':
                    if val.tocode() != target_val.nextnodes[0].tocode():
                        return False
                else:
                    return False
            return True

        functable = {}
        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            if not 'Reg' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            functable[tk, bit] = splitter.split(target_tree)
        ft_order = collections.OrderedDict(sorted(functable.items(), key=lambda t: t[0]))

        invert_regs = []
        for cnt in range(len(ft_order.keys()) - 1):
            for target_cnt in range(cnt + 1, len(ft_order.keys())):#roop for same formal branch
                if ft_order.values()[cnt].keys() != ft_order.values()[target_cnt].keys(): break #not same branch
                if judge_invert_reg(ft_order.values()[cnt].values(), ft_order.values()[target_cnt].values()):
                    invert_regs.append((ft_order.keys()[cnt], ft_order.keys()[target_cnt]))
        if invert_regs:
            print('Invert reg pairs: '+ str(invert_regs))
        else:
            print('There isn\'t invert reg pair.')
        return invert_regs

if __name__ == '__main__':
    codeclone_finder = CodeCloneFinder("../testcode/reg_clone.v")
    codeclone_finder.search_invert_regs()
    codeclone_finder.search_regclone()


