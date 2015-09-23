#-------------------------------------------------------------------------------
# metrics_calculator.py
#
#Calculate comde metrics for register level, function level and module level.
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyverilog.utils.util import getScope
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import dataflow_facade, out_as_html

import pyverilog.controlflow.splitter as splitter


class MetricsCalculator(dataflow_facade):

    def __init__(self, code_file_name, topmodule='TOP', parameter_file='', result_file='metrics.log'):
        """[FUNCTIONS]
        code_file_name: calculation target(verilog file)
        parameter_file: metrics calculation parameter file
        result_file: metrics calculation result
        """
        dataflow_facade.__init__(self, code_file_name, topmodule=topmodule)
        self.result_file_name = result_file
        self.function_metrics_elements = {}

        #initialize parameters for module metrics
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
        #initialize parameters for module metrics
        reg_elements.coef_for_branch = 1
        reg_elements.pow_for_branch = 1
        reg_elements.coef_for_nest = 1
        reg_elements.pow_for_nest = 2
        #initialize parameters for function metrics
        func_elements.coef_for_var = 2
        func_elements.pow_for_var = 1
        #iniatialize parameters for display
        self.module_disp_limit = 10
        self.func_disp_limit = 20
        self.reg_disp_limit = 20

        if hasattr(self, 'config_file'):
            self.config_calc_para_by_file()

    def config_calc_para_by_file(self):
        """ [FUNCTIONS]
        define write_flag, read_flag, write_data, address, read_data for regmap_analyzer.
        """
        try:
            setup_file = open(self.config_file, "r")
            for readline in setup_file:
                if readline[0] == '#': continue
                words = readline.split(':')
                if len(words) == 2:
                    #config parameters for module metrics
                    if words[0] == 'COEF_FOR_INPUT':
                        module_elements.coef_for_input = int(words[1])
                    elif words[0] == 'POW_FOR_INPUT':
                        module_elements.pow_for_input = int(words[1])
                    elif words[0] == 'COEF_FOR_OUTPUT':
                        module_elements.coef_for_output = int(words[1])
                    elif words[0] == 'POW_FOR_OUTPUT':
                        module_elements.pow_for_output = int(words[1])
                    elif words[0] == 'COEF_FOR_REG':
                        module_elements.coef_for_reg = int(words[1])
                    elif words[0] == 'POW_FOR_REG':
                        module_elements.pow_for_reg = int(words[1])
                    elif words[0] == 'COEF_FOR_CLK':
                        module_elements.coef_for_clk = int(words[1])
                    elif words[0] == 'POW_FOR_CLK':
                        module_elements.pow_for_clk = int(words[1])
                    elif words[0] == 'COEF_FOR_RST':
                        module_elements.coef_for_rst = int(words[1])
                    elif words[0] == 'POW_FOR_RST':
                        module_elements.pow_for_rst = int(words[1])

                    #config parameters for module metrics
                    elif words[0] == 'COEF_FOR_BRANCH':
                        reg_elements.coef_for_branch = int(words[1])
                    elif words[0] == 'POW_FOR_BRANCH':
                        reg_elements.pow_for_branch = int(words[1])
                    elif words[0] == 'COEF_FOR_NEST':
                        reg_elements.coef_for_nest = int(words[1])
                    elif words[0] == 'POW_FOR_NEST':
                        reg_elements.pow_for_nest = int(words[1])

                    #config parameters for function metrics
                    elif words[0] == 'COEF_FOR_VAR':
                        func_elements.coef_for_var = int(words[1])
                    elif words[0] == 'NEST_FOR_VAR':
                        func_elements.pow_for_var = int(words[1])

                    #config parameters for display
                    elif words[0] == 'MODULE_DISP_LIMIT':
                        self.module_disp_limit = int(words[1])
                    elif words[0] == 'REG_DISP_LIMIT':
                        self.reg_disp_limit = int(words[1])
                    elif words[0] == 'FUNC_DISP_LIMIT':
                        self.func_disp_limit = int(words[1])
            setup_file.close()
        except IOError:
            print(self.config_file + " can't open for read.")

    def synth_profile(self):
        f_elements_dict = self.calc_function_metrics()
        self.f_profile = function_profile(f_elements_dict, self.func_disp_limit)
        r_elements_dict = self.calc_reg_metrics()
        self.r_profile = reg_profile(r_elements_dict, self.reg_disp_limit)
        m_elements_dict = self.calc_module_metrics()
        self.m_profile = module_profile(m_elements_dict, self.module_disp_limit)

        return self.m_profile, self.r_profile, self.f_profile

    def calc_function_metrics(self):
        func_metrics_elements = {}
        for tv,tk in self.binds.walk_signal():
            if not 'Function' in tv.termtype: continue
            for i, bind in enumerate(self.resolved_binddict[tk]):
                trees = self.binds.extract_all_dfxxx(bind.tree, set([]), 0, DFTerminal)
                if len(trees) > 1: # omit 1 variable function
                    func_metrics_elements[str(getScope(tk)), i] = func_elements()
                    func_metrics_elements[str(getScope(tk)), i].set_var(len(trees))

                    branch_cnt = self.walk_for_count_branch(bind.tree)
                    func_metrics_elements[str(getScope(tk)), i].set_branch_cnt(branch_cnt)

                    _, nest_cnt = self.walk_for_count_nest(bind.tree, count = 1)
                    func_metrics_elements[str(getScope(tk)), i].set_nest_cnt(nest_cnt)
        return func_metrics_elements

    def calc_reg_metrics(self):
        reg_metrics_elements = {}
        for tv, tk in self.binds.walk_signal():
            if not 'Reg' in tv.termtype: continue
            branch_cnt = 0
            if not tk in self.binddict.keys(): continue #no implement reg
            for i, bind in enumerate(self.binddict[tk]):
                reg_metrics_elements[str(getScope(tk)), i] = reg_elements()

                branch_cnt = self.walk_for_count_branch(bind.tree)
                reg_metrics_elements[str(getScope(tk)), i].set_branch_cnt(branch_cnt)

                _, nest_cnt = self.walk_for_count_nest(bind.tree, count = 1)
                reg_metrics_elements[str(getScope(tk)), i].set_nest_cnt(nest_cnt)

        return reg_metrics_elements

    def walk_for_count_branch(self, tree, count=0):
        """ [FUNCTIONS]
        Count up if/else/case branches number for register/function metrics.
        """
        if isinstance(tree, DFBranch):
            count += 1
            count = self.walk_for_count_branch(tree.truenode, count)
            count = self.walk_for_count_branch(tree.falsenode, count)
        return count

    def walk_for_count_nest(self, tree, count=0, max_count=0):
        """ [FUNCTIONS]
        Count up depth of if/else/case nest for register/function metrics.
        """
        if isinstance(tree, DFBranch):
            count += 1
            count, max_count = self.walk_for_count_nest(tree.truenode, count, max_count)
            count -= 1
            count, max_count = self.walk_for_count_nest(tree.falsenode, count, max_count)
        max_count = max_count if count < max_count else count
        return count, max_count

    def calc_module_metrics(self):
        module_metrics_elements = {}
        def initialize_elements_dict():
            for tv, tk in self.binds.walk_signal():
                if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
                if not str(getScope(tk)) in module_metrics_elements.keys():
                    module_metrics_elements[str(getScope(tk))] = module_elements()

        initialize_elements_dict()
        for tv, tk in self.binds.walk_signal():
            if 'Function' in tv.termtype or 'Rename' in tv.termtype: continue
            for eachtype in tv.termtype:
                module_metrics_elements[str(getScope(tk))].add_element(eachtype)
            if 'Reg' in tv.termtype and tk in self.binddict.keys():
                for bvi in self.binddict[tk]:
                    module_metrics_elements[str(getScope(tk))].add_clk(bvi.getClockName())
                    module_metrics_elements[str(getScope(tk))].add_rst(bvi.getResetName())
        return module_metrics_elements

    def decorate_html(html_name):
        temp_html = open('temp.html', 'r')
        out_html = open(html_name, 'w')
        for line in temp_html:
            if 'Module metrics\n' == line or 'Register metrics\n' == line or 'Function metrics\n' == line:
                out_html.write('<Hr color="blue">' + '<font size="5">' + line + '</font>' + '<br>' + '<br>')
            elif '(twice larger than average)' in line:
                out_html.write('<font color="red">' + line + '</font>' + '<br>')
            else:
                out_html.write(line + '<br>')
        temp_html.close()
        out_html.close()

    @out_as_html(decorate_html)
    def show(self):
        if not hasattr(self, 'm_profile'):
            raise Exception('This function must be called after synthesize profile.')
        self.m_profile.show()
        self.r_profile.show()
        self.f_profile.show()

class metrics_profile(object):
    """ [CLASSES]
    Abstract metrics profile for one RTL design.
    This class will be inherited by module/register/function profile.
    """
    def __init__(self, elements_dict, disp_limit=0):
        def sort_by_metrics_score(input_dict):
            return_dict = OrderedDict()
            for key, value in reversed(sorted(input_dict.items(), key=lambda x: x[1])):
                return_dict[key] = value
            return return_dict

        self.elements_dict = elements_dict
        metrics_dict = {key: elements.calc_metrics()  for key, elements in self.elements_dict.items()}
        self.m_ordered = sort_by_metrics_score(metrics_dict)
        self.disp_limit = disp_limit
        self.level = 'abstract'

    def get_total_score(self):
        return sum(self.m_ordered.values())

    def get_average_score(self):
        if self.m_ordered:
            return self.get_total_score() / len(self.m_ordered.values())
        else:
            return 0

    def show(self):
        """ [FUNCTIONS]
        Display metrics score.
        If disp_limit = 0,all scores are displayed.
        """
        print('\n\n' + self.level + ' metrics\nTotal: ' + str(self.get_total_score()))
        print('Average: ' + str(self.get_average_score()))
        print('\nEach score:')

        cnt = 0
        for key, value in self.m_ordered.items():
            if len(key) > 1:
                print(self.level + ':' + str(key[0]))
            else:
                print(self.level + ':' + str(key))
            if value > 2 * self.get_average_score():
                print('total: ' + str(value) + '(twice larger than average)')
            else:
                print('total: ' + str(value))
            self.elements_dict[key].show()
            cnt += 1
            if cnt == self.disp_limit:
                break

class module_profile(metrics_profile):
    def __init__(self, elements_dict, disp_limit=0):
        metrics_profile.__init__(self, elements_dict, disp_limit)
        self.level = 'Module'

class reg_profile(metrics_profile):
    def __init__(self, elements_dict, disp_limit=0):
        metrics_profile.__init__(self, elements_dict, disp_limit)
        self.level = 'Register'

class function_profile(metrics_profile):
    def __init__(self, elements_dict, disp_limit=0):
        metrics_profile.__init__(self, elements_dict, disp_limit)
        self.level = 'Function'

class metrics_elements(object):
    def calc_metrics(self): pass

class reg_elements(metrics_elements):
    """ [CLASSES]
    Elements for calculating one register metrics.
    """
    def __init__(self):
        self.if_nest_num = 0
        self.if_num = 0

    def set_branch_cnt(self, branch_cnt):
        self.branch_cnt = branch_cnt

    def set_nest_cnt(self, nest_cnt):
        self.nest_cnt = nest_cnt

    def calc_metrics(self):
        return ((self.branch_cnt * self.coef_for_branch) ** self.pow_for_branch +
                (self.nest_cnt * self.coef_for_nest) ** self.pow_for_nest)

    def show(self):
        print('Number of branch: ' + str(self.branch_cnt))
        print('Max nest: ' + str(self.nest_cnt))

class func_elements(reg_elements):
    """ [CLASSES]
    Elements for calculating one function metrics.
    """
    def __init__(self):
        self.var_num = 0

    def set_var(self, var_num):
        self.var_num = var_num

    def calc_metrics(self):
        return (self.var_num * self.coef_for_var) ** self.pow_for_var + reg_elements.calc_metrics(self)

    def show(self):
        print('Number of branch: ' + str(self.branch_cnt))
        print('Max nest: ' + str(self.nest_cnt))
        print('Number of variables: ' + str(self.var_num))

class module_elements(metrics_elements):
    """ [CLASSES]
    Elements for calculating one module metrics.
    """
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

    def show(self):
        print('Number of input ports: ' + str(self.input_num))
        print('Number of output ports: ' + str(self.output_num))
        print('Number of registers:  ' + str(self.reg_num))
        print('Number of clocks: ' + str(len(self.clks)))
        print('Number of resets:  ' + str(len(self.rsts)))

if __name__ == '__main__':
    c_m = MetricsCalculator("../testcode/metrics_func.v")
    c_m.synth_profile()
    #c_m.html_name='log.html'
    c_m.show()

