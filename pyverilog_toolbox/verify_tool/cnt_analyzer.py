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
from pyverilog_toolbox.verify_tool.bindlibrary import *

import pyverilog.controlflow.splitter as splitter


class CntAnalyzer(dataflow_facade):

    def analyze_cnt(self):
        self.make_term_ref_dict()
        self.cnt_dict = {}

        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            if not 'cnt' in str(tk) and not 'count' in str(tk): continue
            if not self.binds.eval_value(tv.msb): continue #1bit signal is not counter.

            target_tree = self.makeTree(tk)
            funcdict = splitter.split(target_tree)
            funcdict = splitter.remove_reset_condition(funcdict)

            up_cond = self.filter(funcdict, self.active_ope, op = 'Plus')
            up_cond = {conds[-1] for conds in up_cond.keys()}
            down_cond = self.filter(funcdict, self.active_ope, op = 'Minus')
            down_cond = {conds[-1] for conds in down_cond.keys()}

            new_counter = self.cnt_factory(str(tk), up_cond, down_cond)
            new_counter.set_msb(self.binds.eval_value(tv.msb))
            new_counter.set_reset_value(self.get_reset_value(str(tk), target_tree, str(bvi.getResetName())))

            load_const_dict = self.filter(funcdict, self.active_load_const)
            load_const_dict = {conds[-1] : self.binds.eval_value(value) for conds, value in load_const_dict.items()}
            new_counter.set_load_const_cond(load_const_dict)
            new_counter.set_max_load_const(max(load_const_dict.values()))
            new_counter.make_load_dict(self.binds)
            new_counter.make_change_cond(self.binds)
            self.cnt_dict[new_counter.name] = new_counter

        for cnt_name, counter in self.cnt_dict.items():
            for child_cnt in self.term_ref_dict[cnt_name] & set(self.cnt_dict.keys()) - set([cnt_name]):
                self.cnt_dict[child_cnt].mother_cnts.add(cnt_name)

        for counter in self.cnt_dict.values():
            print counter.tostr() + '\n'

        return self.cnt_dict

    def make_cnt_event_all(self):
        """ [FUNCTIONS] make cnt_event_dict[(cnt_val, operator)]
        ex.
        always @(posedge CLK or negedge RSTN) begin
            if(!RSTN) begin
                reg1 <= 0;
            end else if(cnt == 2'd3) begin
                reg1 <= 1'd1;
            end else begin
                reg1 <= 0;
            end
        end
        cnt_event_dict[3,'Eq)] = (reg1 <= 1'd1,)
        """

        m_setter = MothernodeSetter(self.binds)

        for cnt_name, counter in self.cnt_dict.items():
            cnt_ref_dict = {}
            for term_name in self.term_ref_dict[cnt_name]:
                if term_name == cnt_name: continue
                scope = self.binds.get_scope(term_name)
                target_tree = self.makeTree(scope)
                funcdict = splitter.split(target_tree)
                funcdict = splitter.remove_reset_condition(funcdict)
                branch_dict = {func[-1]: value for func, value in funcdict.items()}#extract last condition

                for branch, value in branch_dict.items():
                    cnt_ref_branch=[]
                    ref_cnt_set = set([])
                    ref_cnt_set = ref_cnt_set | m_setter.extract_all_dfxxx(branch, set([]), 0, pyverilog.dataflow.dataflow.DFTerminal)
                    ref_cnt_set = set([term[0] for term in ref_cnt_set])
                    ref_cnt_set = set([term for term in ref_cnt_set if str(term) == cnt_name])
                    cnt_ref_branch.append((ref_cnt_set, value))
                cnt_ref_dict[term_name] = cnt_ref_branch
            #print cnt_name, cnt_ref_dict
            counter.make_cnt_event_dict(cnt_ref_dict)

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
        self.mother_cnts = set([])
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

    def make_cnt_event_dict(self, cnt_ref_dict):
        """ [FUNCTIONS]
            cnt_ref_branch.append((ref_cnt_set, value))
            cnt_ref_dict[term_name] = cnt_ref_branch
            cnt_event_dict[num] = term_name + "=" + value.tocode()
        """
        self.cnt_event_dict = {}
        for term_name, ref_cnt_set in cnt_ref_dict.items():
            for ref_cnt,value in ref_cnt_set:
                if len(ref_cnt) != 1:
                    raise Exception('Found redundunt condition description @' + term_name)
                ref_cnt = tuple(ref_cnt)[0]

                if str(ref_cnt.mother_node) in self.compare_ope:
                    root_ope = ref_cnt.mother_node
                    cond_lsb = 0
                    diff_list = [1,]
                elif isinstance(ref_cnt.mother_node, pyverilog.dataflow.dataflow.DFPartselect):
                    if str(ref_cnt.mother_node.mother_node) in compare_ope:
                        root_ope = ref_cnt.mother_node.mother_node
                        cond_lsb = ref_cnt.mother_node.lsb
                    if ref_cnt.mother_node.msb == self.msb:
                        diff_list = [1,]
                    else:
                        diff_list = [i for i in range(1,self.msb - ref_cnt.mother_node.msb)]
                else:
                    continue

            if str(root_ope.nextnodes[0]) == str(ref_cnt.name):
                comp_pair = eval_value(root_ope.nextnodes[1])
            elif str(root_ope.nextnodes[1]) == str(ref_cnt.name):
                comp_pair = eval_value(root_ope.nextnodes[0])
            num_list = [comp_pair * (2 ** cond_lsb) * diff for diff in diff_list]
            for num in num_list:
                if num not in self.cnt_event_dict.keys():
                    self.cnt_event_dict[num] = []
                self.cnt_event_dict[num].append(term_name + '=' + value.tocode() + ' @' + root_ope.tocode())
        #print self.name, self.cnt_event_dict

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
        return ("name: " + self.name +
                "\ncategory: " + self.category +
                "\nreset val: " + str(self.reset_value) +
                "\nmax_val: " + str(self.calc_cnt_period()) +
                "\nmother counter:" + str(self.mother_cnts))

class up_down_cnt_profile(cnt_profile):
    def __init__(self, name, up_cond, down_cond):
        self.name = name
        self.up_cond = up_cond
        self.down_cond = down_cond
        self._set_category()
    def _set_category(self):
        self.category = 'up/down counter'
##    def tostr(self):
##        return (cnt_profile.tostr(self) +
##                "\nplus cond:" + str(self.up_cond) +
##                "\nminus cond:" + str(self.down_cond))
class up_cnt_profile(cnt_profile):
    def _set_category(self):
        self.category = 'up counter'
##    def tostr(self):
##        return (cnt_profile.tostr(self) +
##                "\nplus cond:" + str(self.change_dict))
class down_cnt_profile(cnt_profile):
    def _set_category(self):
        self.category = 'down counter'
    def calc_cnt_period(self):
        if self.load_const_cond and self.load_const_cond.values():
            return max(self.load_const_cond.values()) - 1
        return 2 ** (self.msb + 1) - 1
##    def tostr(self):
##        return (cnt_profile.tostr(self) +
##                "\nminus cond:" + str(self.change_cond))

if __name__ == '__main__':
    cnt_analyzer = CntAnalyzer("../testcode/norm_cnt2.v")
    cnt_analyzer.analyze_cnt()
    cnt_analyzer.make_cnt_event_all()
    for counter in cnt_analyzer.cnt_dict.values():
        print counter.name, counter.cnt_event_dict

