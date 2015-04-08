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


class CntAnalyzer(dataflow_facade):

    def analyze_cnt(self):

        binds = self.binds
        for tv,tk,bvi,bit,term_lsb in binds.walk_reg_each_bit():
            if not 'cnt' in str(tk): continue
            print tk

            target_tree = self.makeTree(tk)
            funcdict = splitter.split(target_tree)
            funcdict = splitter.remove_reset_condition(funcdict)
            up_cond = self.filter(funcdict,tv,self.active_ope,op = 'Plus')
            down_cond = self.filter(funcdict,tv,self.active_ope,op = 'Minus')
            new_counter = self.cnt_factory(str(tk), up_cond, down_cond)
            new_counter.set_msb(binds.eval_value(tv.msb))
            new_counter.set_reset_value(self.get_reset_value(str(tk), target_tree, str(bvi.getResetName())))
            new_counter.set_load_const_cond(self.search_load_const_cond(funcdict))
            print new_counter.tostr()
            #tree_list = binds.extract_all_dfxxx(target_tree, set([]), bit - term_lsb, pyverilog.dataflow.dataflow.DFTerminal)

        return

    def get_reset_value(self, cnt_name, target_tree, reset_name):
        if target_tree.condnode.operator == 'Ulnot':
            reset_from_tree = str(target_tree.condnode.nextnodes[0])
        else:
            reset_from_tree = str(target_tree.condnode)
        assert reset_from_tree == reset_name
        return self.binds.eval_value(target_tree.truenode)

    def search_ope_cond(self, funcdict, ope):
        for conds, top_tree in funcdict.items():
            if isinstance(top_tree, pyverilog.dataflow.dataflow.DFOperator) and top_tree.operator == ope:
                return ";".join([cond.tostr() for cond in conds])
        return None

    def filter(self, funcdict, termname, condition, **kwargs):
        ret_funcdict = {}
        for condlist, func in funcdict.items():
            if not condition(termname, func, **kwargs): continue
            ret_funcdict[condlist] = func
        return ret_funcdict

    def active_ope(self, termname, node, **kwargs):
        if 'op' in kwargs.keys():
            return isinstance(node, pyverilog.dataflow.dataflow.DFOperator) and node.operator == kwargs['op']
        raise Exception('Need op arg.')

    def search_load_const_cond(self, funcdict):
        load_const_dict = {}
        for conds, top_tree in funcdict.items():
            if isinstance(top_tree, pyverilog.dataflow.dataflow.DFIntConst) or isinstance(top_tree, pyverilog.dataflow.dataflow.DFEvalValue):
                tree_list = self.binds.extract_all_dfxxx(top_tree, set([]), 0, pyverilog.dataflow.dataflow.DFTerminal)
                if self.binds.eval_value(top_tree) not in load_const_dict.keys():
                    load_const_dict[self.binds.eval_value(top_tree)] = []
                load_const_dict[self.binds.eval_value(top_tree)].append(conds[-1])#ignore false cond
        return load_const_dict

    def cnt_factory(self, name, up_cond, down_cond):
        if up_cond and down_cond:
            return up_down_cnt_profile(name, up_cond, down_cond)
        elif up_cond:
            return up_cnt_profile(name, up_cond)
        elif down_cond:
            return up_cnt_profile(name, down_cond)
        else:
            raise Exception(self.name + ' is irregular counter.')

class cnt_profile(object):
    def __init__(self, name, change_cond):
        self.name = name
        self.change_cond = change_cond
        self._set_category()
    def _set_category(self):
        self.category = 'abstract counter'
        raise Exception('this method must be overridden.')
    def set_reset_value(self, value):
        self.reset_value = value
    def set_load_const_cond(self, load_const_cond):
        self.load_const_cond = load_const_cond
    def get_max_const(self):
        if 0 in self.load_const_cond.keys():
            for cond in self.load_const_cond[0]:
                print cond.tostr()
        else:
            return 2 ** (self.msb + 1) - 1

    def set_msb(self, msb):
        self.msb = msb
    def tostr(self):
        return ("category: " + self.category +
                "\nreset val: " + str(self.reset_value) +
                "\nmax_val: " + str(self.get_max_const()))

class up_down_cnt_profile(cnt_profile):
    def __init__(self, name, up_cond, down_cond):
        self.name = name
        self.up_cond = up_cond
        self.down_cond = down_cond
        self._set_category()
    def _set_category(self):
        self.category = 'up/down counter'
    def tostr(self):
        return (cnt_profile.tostr(self) +
                "\nplus cond:" + str(self.up_cond) +
                "\nminus cond:" + str(self.down_cond))
class up_cnt_profile(cnt_profile):
    def _set_category(self):
        self.category = 'up counter'
    def tostr(self):
        return (cnt_profile.tostr(self) +
                "\nplus cond:" + str(self.change_cond))
class down_cnt_profile(cnt_profile):
    def _set_category(self):
        self.category = 'down counter'
    def tostr(self):
        return (cnt_profile.tostr(self) +
                "\nminus cond:" + str(self.change_cond))

if __name__ == '__main__':
    cnt_analyzer = CntAnalyzer("../testcode/norm_cnt2.v")
    cnt_analyzer.analyze_cnt()
