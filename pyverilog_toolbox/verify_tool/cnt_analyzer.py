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
        cnt_dict = {}
        binds = self.binds
        for tv,tk,bvi,bit,term_lsb in binds.walk_reg_each_bit():
            if not 'cnt' in str(tk) and not 'count' in str(tk): continue
            if not binds.eval_value(tv.msb): continue #1bit signal is not counter.
            print tk

            target_tree = self.makeTree(tk)
            funcdict = splitter.split(target_tree)
            funcdict = splitter.remove_reset_condition(funcdict)

            up_cond = self.filter(funcdict, self.active_ope, op = 'Plus')
            up_cond = {conds[-1] for conds in up_cond.keys()}
            down_cond = self.filter(funcdict, self.active_ope, op = 'Minus')
            down_cond = {conds[-1] for conds in down_cond.keys()}

            new_counter = self.cnt_factory(str(tk), up_cond, down_cond)
            new_counter.set_msb(binds.eval_value(tv.msb))
            new_counter.set_reset_value(self.get_reset_value(str(tk), target_tree, str(bvi.getResetName())))

            load_const_dict = self.filter(funcdict, self.active_load_const)
            load_const_dict = {conds[-1] : binds.eval_value(value) for conds, value in load_const_dict.items()}
            new_counter.set_load_const_cond(load_const_dict)
            new_counter.set_max_load_const(max(load_const_dict.values()))
            new_counter.make_load_dict(binds)
            new_counter.make_change_cond(binds)
            print new_counter.tostr()
            cnt_dict[new_counter.name] = new_counter

        return cnt_dict

    def get_reset_value(self, cnt_name, target_tree, reset_name):
        if target_tree.condnode.operator == 'Ulnot':
            reset_from_tree = str(target_tree.condnode.nextnodes[0])
        else:
            reset_from_tree = str(target_tree.condnode)
        assert reset_from_tree == reset_name
        return self.binds.eval_value(target_tree.truenode)

    def filter(self, funcdict, condition, **kwargs):
        ret_funcdict = {}
        for condlist, func in funcdict.items():
            if not condition(func, **kwargs): continue
            ret_funcdict[condlist] = func
        return ret_funcdict

    def active_ope(self, node, **kwargs):
        if 'op' in kwargs.keys():
            return isinstance(node, pyverilog.dataflow.dataflow.DFOperator) and node.operator == kwargs['op']
        raise Exception('Need op arg.')

    def active_load_const(self, node):
        return (isinstance(node, pyverilog.dataflow.dataflow.DFIntConst) or
                isinstance(node, pyverilog.dataflow.dataflow.DFEvalValue))

    def cnt_factory(self, name, up_cond, down_cond):
        if up_cond and down_cond:
            return up_down_cnt_profile(name, up_cond, down_cond)
        elif up_cond:
            return up_cnt_profile(name, up_cond)
        elif down_cond:
            return down_cnt_profile(name, down_cond)
        else:
            raise Exception(name + ' is irregular counter.')

class cnt_profile(object):
    compare_ope = ('Eq', 'NotEq', 'GreaterEq', 'LessEq', 'GreaterThan', 'LessThan')
    plus_ope = ('NotEq', 'LessEq', 'LessThan')
    load_ope = ('Eq', 'GreaterEq', 'GreaterThan')
    eq_ope = ('Eq', 'GreaterEq', 'LessEq')

    def __init__(self, name, change_dict):
        self.name = name
        self.change_dict = change_dict
        self._set_category()
    def _set_category(self):
        self.category = 'abstract counter'
        raise Exception('this method must be overridden.')
    def set_reset_value(self, value):
        self.reset_value = value
    def set_load_const_cond(self, load_const_cond):
        self.load_const_cond = load_const_cond
    def set_max_load_const(self, max_load_const):
        """ [FUNCTIONS]
        ex.
        if(up_cnt >= 3'd7) begin
            up_cnt <= 3;
        end else if(up_cnt >= 3'd7) begin
            up_cnt <= 5;

        self.max_load_const = 5
        """
        self.max_load_const = max_load_const
    def make_load_dict(self, binds):
        """ [FUNCTIONS]
        self.load_dict[load_const] = (cnt value when load execute)
        if prulal condition for same load_const, only store max value.
        ex.

        if(up_cnt >= 3'd7) begin
            up_cnt <= 0;
        end else if(up_cnt >= 3'd7) begin
            up_cnt <= 0;

        self.load_dict[0] = 7
        """
        self.load_dict = {}
        for cond, value in self.load_const_cond.items():
            if value != 0 and value != self.max_load_const: continue
            tree_list = binds.extract_all_dfxxx(cond, set([]), 0, pyverilog.dataflow.dataflow.DFOperator)
            tree_list = set([tree for tree in tree_list if tree[0].operator in self.load_ope])
            for tree, bit in tree_list:
                if str(tree.nextnodes[0]) == self.name:
                    cnt_cond = binds.eval_value(tree.nextnodes[1])
                elif str(tree.nextnodes[1]) == self.name:
                    cnt_cond = binds.eval_value(tree.nextnodes[0])
                else:
                    continue
                if value in self.load_dict.keys() and self.load_dict[value][1] > cnt_cond:
                    continue
                self.load_dict[value] = (tree.operator, cnt_cond)

        print self.load_dict

    def make_change_cond(self, binds):
        for cond in self.change_dict:
            tree_list = binds.extract_all_dfxxx(cond, set([]), 0, pyverilog.dataflow.dataflow.DFOperator)
            tree_list = set([tree for tree in tree_list if tree[0].operator in self.plus_ope])
            for tree, bit in tree_list:
                if str(tree.nextnodes[0]) == self.name:
                    change_limit_num = binds.eval_value(tree.nextnodes[1])
                elif str(tree.nextnodes[1]) == self.name:
                    change_limit_num = binds.eval_value(tree.nextnodes[0])
                else:
                    continue
                if not hasattr(self, 'change_cond') or self.change_cond[1] < change_limit_num:
                    self.change_cond = (tree.operator , change_limit_num)

    def calc_cnt_period(self):
        if hasattr(self, 'change_cond'):
            if self.change_cond[0] in self.eq_ope:
                return self.change_cond[1]
            else:
                return self.change_cond[1] - 1
        elif self.load_dict[0]:
            if self.load_dict[0][0] in self.eq_ope:
                return self.load_dict[0][1]
            else:
                return self.load_dict[0][1] - 1
        return 2 ** (self.msb + 1) - 1 #freerun

    def set_msb(self, msb):
        self.msb = msb
    def tostr(self):
        return ("category: " + self.category +
                "\nreset val: " + str(self.reset_value) +
                "\nmax_val: " + str(self.calc_cnt_period()))

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
                "\nplus cond:" + str(self.change_dict))
class down_cnt_profile(cnt_profile):
    def _set_category(self):
        self.category = 'down counter'
    def calc_cnt_period(self):
        if self.load_const_cond and self.load_const_cond.values():
            return max(self.load_const_cond.values()) - 1
        return 2 ** (self.msb + 1) - 1
    def tostr(self):
        return (cnt_profile.tostr(self) +
                "\nminus cond:" + str(self.change_cond))

if __name__ == '__main__':
    cnt_analyzer = CntAnalyzer("../testcode/norm_cnt2.v")
    cnt_analyzer.analyze_cnt()
