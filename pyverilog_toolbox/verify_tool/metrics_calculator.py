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


class MetricsCalculator(dataflow_facade):

    def __init__(self, code_file_name, parameter_file='', result_file='metrics.log'):
        """[FUNCTIONS]
        code_file_name: calculation target(verilog file)
        parameter_file: metrics calculation parameter file
        result_file: metrics calculation result
        """
        dataflow_facade.__init__(self, code_file_name)
        self.result_file_name = result_file

        self.module_metrics_elements = {}
        self.reg_metrics_elements = {}
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

    def calc_metrics(self):
        """[FUNCTIONS]
        Calculating verilog code metrics.
        """
        m_metrics_dict = self.calc_module_metrics()
        return m_metrics_dict, None, None

    # TODO
    def calc_reg_metrics(self):
        pass

    def calc_module_metrics(self):
        def initialize_elements_dict():
            for tv,tk in self.binds.walk_signal():
                if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
                if not str(getScope(tk)) in self.module_metrics_elements.keys():
                    self.module_metrics_elements[str(getScope(tk))] = module_elements()

        initialize_elements_dict()
        for tv,tk in self.binds.walk_signal():
            if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
            for eachtype in tv.termtype:
                self.module_metrics_elements[str(getScope(tk))].add_element(eachtype)
            if 'Reg' in tv.termtype and tk in self.binddict.keys():
                for bvi in self.binddict[tk]:
                    self.module_metrics_elements[str(getScope(tk))].add_clk(bvi.getClockName())
                    self.module_metrics_elements[str(getScope(tk))].add_rst(bvi.getResetName())

        for module, elements in self.module_metrics_elements.items():
            print str(module) + ': ' + str(elements.calc_metrics())
        return { str(module):elements.calc_metrics()  for module, elements in self.module_metrics_elements.items()}


class metrics_elements(object):
    def calc_metrics(self): pass
    def add_element(self): pass

class reg_elements(metrics_elements):
    def __init__(self):
        self.if_nest_num = 0
        self.if_num = 0
        self.var_num = 0

class module_elements(object):

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

if __name__ == '__main__':
    c_m = MetricsCalculator("../testcode/metrics_test.v")
    c_m.calc_metrics()



