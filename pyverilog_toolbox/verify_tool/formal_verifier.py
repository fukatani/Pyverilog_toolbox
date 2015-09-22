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

from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import dataflow_facade
from pyverilog_toolbox.verify_tool.bindlibrary import eval_value
from sympy import Symbol, sympify
from types import MethodType
from pyverilog.utils.util import toTermname

import pyverilog.utils.op2mark as op2mark

class FormalVerifier(dataflow_facade):

    def __init__(self, code_file_name, topmodule=''):
        dataflow_facade.__init__(self, code_file_name, topmodule=topmodule)
        t_manager = term_manager()
        t_manager.set_scope_dict(self.binds.scope_dict)
        t_manager.set_terms(self.binds._terms)

        DFBranch.tocode_org = MethodType(DFBranch.tocode, None, DFBranch)
        DFBranch.tocode = MethodType(DFBranch_tocode, None, DFBranch)
        DFOperator.tocode_org = MethodType(DFOperator.tocode, None, DFOperator)
        DFOperator.tocode = MethodType(DFOperator_tocode, None, DFOperator)
        DFOperator.is_reduction = MethodType(DFOperator_is_reduction, None, DFOperator)
        DFOperator.is_algebra = MethodType(DFOperator_is_algebra, None, DFOperator)
        DFTerminal.tocode_org = MethodType(DFTerminal.tocode, None, DFTerminal)
        DFTerminal.tocode = MethodType(DFTerminal_tocode, None, DFTerminal)

    def write_back_DFmethods(self):
        DFTerminal.tocode = MethodType(DFTerminal.tocode_org, None, DFTerminal)
        DFBranch.tocode = MethodType(DFBranch.tocode_org, None, DFBranch)
        DFOperator.tocode = MethodType(DFOperator.tocode_org, None, DFOperator)
        del DFOperator.tocode_org
        del DFOperator.is_reduction
        del DFOperator.is_algebra

    def calc_truth_table(self, var_name):
        """[FUNCTIONS]
        Wrapper for _calc_truth_table (for assuring execute write_back_DFmethods.)
        """
        try:
            truth_table = self._calc_truth_table(var_name)
        finally:
            self.write_back_DFmethods()
        return truth_table

    def _declare_symbols(self, tree_names):
        symbols = {}
        for tree in tree_names:
            symbol_name = tree.replace('.', '_')
            scope = toTermname(str(tree))
            term = self.terms[scope]
            msb = eval_value(term.msb)
            lsb = eval_value(term.lsb)
            if msb == lsb:
                symbols[symbol_name] = Symbol(symbol_name)
            else:
                for i in range(lsb, msb + 1):
                    symbol_name_bit = term_manager().publish_new_name(symbol_name, i)
                    symbols[symbol_name_bit] = Symbol(symbol_name_bit)

        symbols = self._declare_renamed_symbols(symbols)
        return symbols

    def _declare_renamed_symbols(self, symbols):
        for signal in term_manager().renamed_signals:
            signal = signal.replace('.', '_')
            symbols[signal] = Symbol(signal)
        return symbols

    def _delete_renamed_symbols(self, symbols):
        """ [FUNCTIONS]
        For not assined constant value to tree under algebra.
        """
        for signal in term_manager().renamed_signals:
            signal = signal.replace('.', '_')
            symbols.pop(signal)
        return symbols

    def _make_expr(self, target_tree):
        """ [FUNCTIONS]
        Make expr and symbols.
        expr: sympy expression
        symbol: sympy variable
        """
        term_manager().flash_renamed_signals()
        trees = self.binds.extract_all_dfxxx(target_tree, set([]), 0, DFTerminal)
        tree_names = [str(tree[0]) for tree in trees]
        expr_str = self.to_sympy_expr(target_tree.tocode())
        symbols = self._declare_symbols(tree_names)
        expr = sympify(expr_str, symbols, convert_xor=False)
        symbols = self._delete_renamed_symbols(symbols)  #to not assign const value to algebra
        return expr, symbols

    def _calc_truth_table(self, var_name):
        """[FUNCTIONS]
        Sweep variable and calculate trutu_table.
        """
        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            if str(tk) != var_name: continue

            target_tree = self.makeTree(tk)
            msb = eval_value(tv.msb)
            lsb = eval_value(tv.lsb)
            #TODO case of multi bit (not algebra)
            expr, symbols = self._make_expr(target_tree)

            truth_table = {}
            for result, var_state in self.walk_truth_table(symbols, expr):
                truth_table[str(var_state)] = result
                print('result:' + str(result) + '@' + str(var_state))
        return truth_table

    def walk_truth_table(self, symbols, expr):
        init_expr = expr
        for cnt in range(0, 2 ** len(symbols.keys())):
            expr = init_expr
            var_state = []
            for i, var in enumerate(sorted(symbols.keys(), key=lambda t: str(t))):
                value = (format(cnt, 'b').zfill(len(symbols.keys()))[i]) == '1'
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
        replace_words = (('!', '~'), ('||', '|'), ('&&', '&'), ('==', '^~'),
                         ('!=', '^'), )
        for comb in replace_words:
            expr = expr.replace(comb[0], comb[1])
        return expr

def DFBranch_tocode(self, dest='dest', always=''):
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

def DFOperator_is_algebra(self):
    if self.operator in ('Plus', 'Minus', 'LessThan', 'GreaterThan', 'LessEq', 'GreaterEq'):
        return True
    else:
        return False

def DFTerminal_tocode(self, dest='dest'):
    if term_manager().is_under_algebra:
        return term_manager().publish_new_name(str(self)).replace('.', '_')
    else:
        return self.tocode_org()

def DFOperator_tocode(self):
    if self.is_algebra():  #if operator is algebra, nextnodes aren't sweeped.
        term_manager().set_is_under_algebra(True)
        code = self.tocode_org()
        term_manager().set_is_under_algebra(False)
        return code
    elif self.is_reduction():
        if isinstance(self.nextnodes[0], DFPartselect):
            term = self.nextnodes[0].var
            msb = eval_value(self.nextnodes[0].msb)
            lsb = eval_value(self.nextnodes[0].lsb)
        elif isinstance(self.nextnodes[0], DFTerminal):
            term = term_manager().get_term(str(self.nextnodes[0]))
            msb = eval_value(term.msb)
            lsb = eval_value(term.lsb)
        else:
            raise Exception('Unexpected exception.')
        mark = op2mark.op2mark(self.operator)
        return mark.join([term_manager().publish_new_name(str(term), i).replace('.', '_') for i in range(lsb, msb + 1)])
    else:
        return self.tocode_org()

class term_manager(object):
    """ [CLASSES]
        Singleton class for manage terminals for DFxxx.
    """
    _singleton = None
    def __new__(cls, *argc, **argv):
        if cls._singleton == None:
            cls._singleton = object.__new__(cls)
            cls.is_under_algebra = False
            cls.renamed_signals = []
        return cls._singleton

    def set_scope_dict(self, scope_dict):
        self.scope_dict = scope_dict

    def set_terms(self, terms):
        self.terms = terms

    def get_term(self, signal):
        scope = toTermname(signal)
        return self.terms[scope]

    def set_is_under_algebra(self, flag=False):
        self.is_under_algebra = flag

    def publish_new_name(self, signal, bit=None):
        if bit is None:
            new_name = signal + '_'
        else:
            new_name = signal + '__' + str(bit) + '__'
        while new_name in self.scope_dict.keys():
            new_name += '_'
        if bit is None:
            self.renamed_signals.append(new_name)
        return new_name

    def flash_renamed_signals(self):
        self.renamed_signals = []

if __name__ == '__main__':
    fv = FormalVerifier("../testcode/fv_test.v")
    fv.calc_truth_table('TOP.I')

