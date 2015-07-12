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
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import pyverilog.utils.version
from pyverilog.utils.util import *
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import *
from pyverilog_toolbox.verify_tool.bindlibrary import *

import pyverilog.controlflow.splitter as splitter


class MetricsCalculator(dataflow_facade):

    def __init__(self, code_file_name, parameter_file='', result_file='metrics.log'):
        """[FUNCTIONS]
        code_file_name: calculation target(verilog file)
        parameter_file: metrics calculation parameter file
        result_file: metrics calculation result
        """
        dataflow_facade.__init__(self, code_file_name)
        self.result_file_name = result_file
        self.function_metrics_elements = {}

        #initializing parameters for module metrics
        module_elements.coef_for_input = 3
        module_elements.pow_for_input = 1
        module_elements.coef_for_output = 3
        module_elements.pow_for_output = 1
        module_elements.coef_for_reg = 1
        module_elements.pow_for_reg = 1
        module_elements.coef_for_clk = 2
        module_elements.pow_for_clk = 2
        module_elements.coef_for_rst = 2
        module_elements.pow_for_rst = 1
        #initializing parameters for module metrics
        reg_elements.coef_for_branch = 1
        reg_elements.pow_for_branch = 1
        reg_elements.coef_for_nest = 1
        reg_elements.pow_for_nest = 2
        #initializing parameters for function metrics
        func_elements.coef_for_var = 2
        func_elements.pow_for_var = 1

    def calc_metrics(self):
        """[FUNCTIONS]
        Calculating verilog code metrics.
        Each metrics is returned as Dict(Order by metrics).
        """
        def sort_by_metrics_score(input_dict):
            return_dict = OrderedDict()
            for key, value in reversed(sorted(input_dict.items(), key=lambda x:x[1])):
                return_dict[key] = value
            return return_dict

        f_metrics_dict = self.calc_function_metrics()
        f_m_ordered = sort_by_metrics_score(f_metrics_dict)

        r_metrics_dict = self.calc_reg_metrics()
        r_m_ordered = sort_by_metrics_score(r_metrics_dict)

        m_metrics_dict = self.calc_module_metrics()
        m_m_ordered = sort_by_metrics_score(m_metrics_dict)

        return m_m_ordered, r_m_ordered, f_m_ordered

    def calc_function_metrics(self):
        func_metrics_elements = {}
        for tv,tk in self.binds.walk_signal():
            if not 'Function' in tv.termtype: continue
            for i, bind in enumerate(self.resolved_binddict[tk]):
                trees = self.binds.extract_all_dfxxx(bind.tree, set([]), 0, pyverilog.dataflow.dataflow.DFTerminal)
                if len(trees) > 1: # omit 1 variable function
                    func_metrics_elements[str(getScope(tk)), i] = func_elements()
                    func_metrics_elements[str(getScope(tk)), i].set_var(len(trees))

                    branch_cnt = self.walk_for_count_branch(bind.tree)
                    func_metrics_elements[str(getScope(tk)), i].set_branch_cnt(branch_cnt)

                    _, nest_cnt = self.walk_for_count_nest(bind.tree, count = 1)
                    func_metrics_elements[str(getScope(tk)), i].set_nest_cnt(nest_cnt)
        return { str(key):elements.calc_metrics()  for key, elements in func_metrics_elements.items()}

    def calc_reg_metrics(self):
        reg_metrics_elements = {}
        for tv,tk in self.binds.walk_signal():
            if not 'Reg' in tv.termtype: continue
            branch_cnt = 0
            if not tk in self.binddict.keys(): continue #no implement reg
            for i, bind in enumerate(self.binddict[tk]):
                reg_metrics_elements[str(getScope(tk)), i] = reg_elements()

                branch_cnt = self.walk_for_count_branch(bind.tree)
                reg_metrics_elements[str(getScope(tk)), i].set_branch_cnt(branch_cnt)

                _, nest_cnt = self.walk_for_count_nest(bind.tree, count = 1)
                reg_metrics_elements[str(getScope(tk)), i].set_nest_cnt(nest_cnt)

        return { str(key):elements.calc_metrics()  for key, elements in reg_metrics_elements.items()}

    def walk_for_count_branch(self, tree, count=0):
        """ [FUNCTIONS]
        Count up if/else/case branches number.
        """
        if isinstance(tree, pyverilog.dataflow.dataflow.DFBranch):
            count += 1
            count = self.walk_for_count_branch(tree.truenode, count)
            count = self.walk_for_count_branch(tree.falsenode, count)
        return count

    def walk_for_count_nest(self, tree, count=0, max_count=0):
        """ [FUNCTIONS]
        Count up depth of if/else/case nest.
        """
        if isinstance(tree, pyverilog.dataflow.dataflow.DFBranch):
            count += 1
            count, max_count = self.walk_for_count_nest(tree.truenode, count, max_count)
            count -= 1
            count, max_count = self.walk_for_count_nest(tree.falsenode, count, max_count)
        max_count = max_count if count < max_count else count
        return count, max_count

    def calc_module_metrics(self):
        module_metrics_elements = {}
        def initialize_elements_dict():
            for tv,tk in self.binds.walk_signal():
                if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
                if not str(getScope(tk)) in module_metrics_elements.keys():
                    module_metrics_elements[str(getScope(tk))] = module_elements()

        initialize_elements_dict()
        for tv,tk in self.binds.walk_signal():
            if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
            for eachtype in tv.termtype:
                module_metrics_elements[str(getScope(tk))].add_element(eachtype)
            if 'Reg' in tv.termtype and tk in self.binddict.keys():
                for bvi in self.binddict[tk]:
                    module_metrics_elements[str(getScope(tk))].add_clk(bvi.getClockName())
                    module_metrics_elements[str(getScope(tk))].add_rst(bvi.getResetName())
        return { str(module):elements.calc_metrics()  for module, elements in module_metrics_elements.items()}


class metrics_elements(object):
    def calc_metrics(self): pass

class reg_elements(metrics_elements):
    def __init__(self):
        self.if_nest_num = 0
        self.if_num = 0
        self.var_num = 0
    def set_branch_cnt(self, branch_cnt):
        self.branch_cnt = branch_cnt
    def set_nest_cnt(self, nest_cnt):
        self.nest_cnt = nest_cnt
    def calc_metrics(self):
        return ((self.branch_cnt * self.coef_for_branch) ** self.pow_for_branch +
                (self.nest_cnt * self.coef_for_nest) ** self.pow_for_nest)

class func_elements(reg_elements):
    def __init__(self):
        self.var_num = 0
    def set_var(self, var_num):
        self.var_num = var_num
    def calc_metrics(self):
        return (self.var_num * self.coef_for_var) ** self.pow_for_var + reg_elements.calc_metrics(self)

class module_elements(metrics_elements):

    def __init__(self):
        self.input_num = 0
        self.output_num = 0
        self.reg_num = 0
        self.clks = set([])
        self.rsts = set([])

    def add_element(self, element_type):
        if element_type == 'Input':
            self.input_num += 1
        elif element_type == 'Output':
            self.output_num += 1
        elif element_type == 'Reg':
            self.reg_num += 1

    def add_clk(self, clk_name):
        self.clks.add(clk_name)

    def add_rst(self, rst_name):
        self.rsts.add(rst_name)

    def calc_metrics(self):
        return ((self.input_num * self.coef_for_input) ** self.pow_for_input +
                (self.output_num * self.coef_for_output) ** self.pow_for_output +
                (self.reg_num * self.coef_for_reg) ** self.pow_for_reg +
                (len(self.clks) * self.coef_for_clk) ** self.pow_for_clk +
                (len(self.rsts) * self.coef_for_rst) ** self.pow_for_rst)

def display_metrics(metrics_dict, disp_limit=0):
    """ [FUNCTIONS]
    Display metrics score.
    If disp_limit = 0,all scores are displayed.
    """
    for key, value in metrics_dict.items():
        print str(key) + ': ' + str(value)

if __name__ == '__main__':
    c_m = MetricsCalculator("../testcode/metrics_test.v")
    m_metrics, r_metrics, f_metrics = c_m.calc_metrics()
    display_metrics(m_metrics)
    display_metrics(r_metrics)
    display_metrics(f_metrics)
