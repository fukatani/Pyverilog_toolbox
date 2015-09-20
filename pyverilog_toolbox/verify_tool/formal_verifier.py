#-------------------------------------------------------------------------------
# formal_verifier.py
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyverilog.utils.util import *
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import *
from pyverilog_toolbox.verify_tool.bindlibrary import *
from sympy import *
from types import MethodType

import pyverilog.controlflow.splitter as splitter
import pyverilog.utils.op2mark as op2mark

class FormalVerifier(dataflow_facade):

    def __init__(self, code_file_name, topmodule=''):
        dataflow_facade.__init__(self, code_file_name, topmodule=topmodule)

        DFBranch.tocode_org = MethodType(DFBranch.tocode, None, DFBranch)
        DFBranch.tocode = MethodType(DFBranch_tocode_for_sympy, None, DFBranch)
        DFOperator.tocode_org = MethodType(DFOperator.tocode, None, DFOperator)
        DFOperator.tocode = MethodType(DFOperator_tocode_for_sympy, None, DFOperator)
        DFOperator.is_reduction = MethodType(DFOperator_is_reduction, None, DFOperator)
        DFTerminal.scope_dict = self.binds.scope_dict
        DFTerminal.terms = self.binds._terms
        DFTerminal.get_bind = MethodType(DFTerminal_get_terms, None, DFTerminal)

    def write_back_DFmethods(self):
        DFBranch.tocode = MethodType(DFBranch.tocode_org, None, DFBranch)
        DFOperator.tocode = MethodType(DFOperator.tocode_org, None, DFOperator)
        del DFOperator.tocode_org
        del DFOperator.is_reduction
        del DFTerminal.scope_dict
        del DFTerminal.terms
        del DFTerminal.get_bind

    def calc_truth_table(self, var_name):
        """[FUNCTIONS]
        """
        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            target_tree = self.makeTree(tk)
            if str(tk) != var_name: continue
            trees = self.binds.extract_all_dfxxx(target_tree, set([]), 0, DFTerminal)
            tree_names = [str(tree[0]) for tree in trees]

            ns = {}
            for tree in tree_names:
                symbol_name = tree.replace('.','_')
                scope = self.binds.scope_dict[tree]
                term = self.terms[scope]
                msb = eval_value(term.msb)
                lsb = eval_value(term.lsb)
                if msb == lsb:
                    ns[symbol_name] = Symbol(symbol_name)
                else:
                    for i in range(lsb, msb + 1):
                        symbol_name_bit = get_bus_name(symbol_name, i)
                        ns[symbol_name_bit] = Symbol(symbol_name_bit)

            f = self.to_sympy_expr(target_tree.tocode())
            expr = sympify(f, ns, convert_xor=False)

            truth_table = {}
            for result, var_state in self.walk_truth_table(ns, expr):
                truth_table[str(var_state)] = result
                print('result:' + str(result) + '@' + str(var_state))
        return truth_table

    def walk_truth_table(self, ns, expr):
        init_expr = expr
        for cnt in range(0, 2 ** len(ns.keys())):
            expr = init_expr
            var_state = []
            for i, var in enumerate(sorted(ns.keys() ,key=lambda t:str(t))):
                value = (format(cnt, 'b').zfill(len(ns.keys()))[i]) == '1'
                var_state.append(var + ': ' + str(value))
                expr = expr.subs(var, value)
            yield expr, var_state

    def to_sympy_expr(self, expr):
        """ [FUNCTIONS]
        verilog operators
        [] : implemented (convert [i] to __i__)
        ! ~ : implemented
        * / % : unsupported
        + -
        << >>
        == != : implemented
        < <= > =>
        & : implemented
        ^ ^~ : implemented
        | : implemented
        && : implemented
        || : implemented
        ? : implemented
        reduction : implemented
        """
        replace_words = (('!', '~'), ('||', '|'), ('&&', '&'), ('==','^~'),
                         ('!=', '^'), )
        for comb in replace_words:
            expr = expr.replace(comb[0], comb[1])
        return expr

def DFBranch_tocode_for_sympy(self, dest='dest', always=''):
    ret = '('
    if self.condnode is not None: ret += '(' + self.condnode.tocode(dest) + ')'
    ret += '& '
    if self.truenode is not None: ret += self.truenode.tocode(dest)
    else: ret += dest
    ret += " | "
    if self.falsenode is not None:
         ret += '(~' + self.condnode.tocode(dest) + '&'
         ret += self.falsenode.tocode(dest) + ')'
    else: ret += dest
    ret += ")"
    return ret

def DFOperator_is_reduction(self):
    if self.operator in ('Uand', 'Uor', 'Uxor', 'Uxnor'):
        return len(self.nextnodes) == 1
    else:
        return False

def DFOperator_tocode_for_sympy(self):
    if not self.is_reduction():
        return self.tocode_org()
    else:
        if isinstance(self.nextnodes[0], DFPartselect):  #TODO
            term = self.nextnodes[0].var
            msb = eval_value(self.nextnodes[0].msb)
            lsb = eval_value(self.nextnodes[0].lsb)
        elif isinstance(self.nextnodes[0], DFTerminal):
            term = self.nextnodes[0].get_bind()
            msb = eval_value(term.msb)
            lsb = eval_value(term.lsb)
        else:
            raise Exception('Unexpected exception.')
        mark = op2mark.op2mark(self.operator)
        return mark.join([get_bus_name(term, i).replace('.', '_') for i in range(lsb, msb + 1)])

def DFTerminal_get_terms(self):
    scope = DFTerminal.scope_dict[str(self)]
    return DFTerminal.terms[scope]

def get_bus_name(signal, bit):
    return str(signal) + '__' + str(bit) + '__'

if __name__ == '__main__':
    fv = FormalVerifier("../testcode/fv_test.v")
    #fv.calc_truth_table('TOP.A')
    #fv.calc_truth_table('TOP.C')
    #fv.calc_truth_table('TOP.E')
    a=fv.calc_truth_table('TOP.G')
    fv.write_back_DFmethods()
    pass
