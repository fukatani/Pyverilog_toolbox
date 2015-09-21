#-------------------------------------------------------------------------------
# codeclone_finder.py
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import dataflow_facade, out_as_html
from pyverilog_toolbox.verify_tool.bindlibrary import eval_value

import pyverilog.controlflow.splitter as splitter


class CodeCloneFinder(dataflow_facade):

    def search_regclone(self):
        """[FUNCTIONS]
        search register pairs that always hold same values.

        ex.
        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg1 <= 1'b0;
            end else begin
                reg1 <= IN;
            end
        end

        assign in1 = IN;

        always @(posedge CLK or negedge RST) begin
            if(RST) begin
                reg2 <= 1'b0;
            end else begin
                reg2 <= in1;
            end
        end
        """
        code_dict = {}
        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            if not 'Reg' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            code_dict[tk, bit] = target_tree.tocode()

        #sort for assign code(same assign reg must line up next to)
        #and assure output order for test: + str(t[0])
        cd_order = OrderedDict(sorted(code_dict.items(), key=lambda t: t[1] + str(t[0])))
        clone_regs = []
        cd_values = list(cd_order.values())
        cd_keys = list(cd_order.keys())
        for cnt in range(len(cd_order.keys()) - 1):
            if cd_values[cnt] == cd_values[cnt + 1]:
                clone_regs.append((cd_keys[cnt], cd_keys[cnt + 1]))

        if clone_regs:
            print('Clone reg pairs:')
            self.deploy_reg_info(clone_regs)
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
                if isinstance(val, DFEvalValue) and isinstance(target_val, DFEvalValue):
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
        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            if not 'Reg' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            functable[tk, bit] = splitter.split(target_tree)
        ft_order = OrderedDict(sorted(functable.items(), key=lambda t: str(t[0])))

        invert_regs = []
        ft_values = list(ft_order.values())
        ft_keys = list(ft_order.keys())
        for cnt in range(len(ft_order.keys()) - 1):
            for target_cnt in range(cnt + 1, len(ft_keys)):#roop for same formal branch
                if ft_values[cnt].keys() != ft_values[target_cnt].keys(): break #not same branch
                if judge_invert_reg(ft_values[cnt].values(), ft_values[target_cnt].values()):
                    invert_regs.append((ft_keys[cnt], ft_keys[target_cnt]))
        if invert_regs:
            print('Invert reg pairs:')
            self.deploy_reg_info(invert_regs)
        else:
            print('There isn\'t invert reg pair.')
        return invert_regs

    def deploy_reg_info(self, regs):
        for reg in regs:
            print(str(reg[0][0]) + '[' + str(reg[0][1]) + '] and ' +
                  str(reg[1][0]) + '[' + str(reg[1][1]) + ']')

    def decorate_html(html_name):
        temp_html = open('temp.html', 'r')
        out_html = open(html_name, 'w')
        for line in temp_html:
            line = line.replace('Clone reg pairs:', '<font size="5">' + 'Clone reg pairs:' + '</font>' + '<br>')
            line = line.replace('Invert reg pairs:', '<Hr>' + '<font size="5">' + 'Invert reg pairs:' + '</font>' + '<br>')
            out_html.write(line + '<br>')
        temp_html.close()
        out_html.close()

    @out_as_html(decorate_html)
    def show(self):
        self.search_regclone()
        self.search_invert_regs()

if __name__ == '__main__':
    CodeCloneFinder("../testcode/reg_clone.v").show()

