#-------------------------------------------------------------------------------
# get_dataflow_facade.py
#
# interface of register map analyzer
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from optparse import OptionParser
import pyverilog.utils.util as util
import pyverilog.dataflow.bindvisitor as BindVisitor
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer
from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.bindlibrary import BindLibrary
from pyverilog.controlflow.controlflow_analyzer import VerilogControlflowAnalyzer

def out_as_html(html_deco):
    def _helper(out_func):
        def __helper(self):
            if hasattr(self, 'html_name'):
                temp_sysout = sys.stdout
                sys.stdout = open('temp.html', 'w')
                return_val = out_func(self)
                sys.stdout.close()
                sys.stdout = temp_sysout
                html_deco(self.html_name)
            else:
                return_val = out_func(self)
            return return_val
        return __helper
    return _helper


def _createAlwaysinfo(self, node, scope):
    """ [FUNCTIONS]
    This function is replaced by BindVisitor._createAlwaysinfo (in bindvisitor.py) in pyverilog_toolbox.
    But this correspondence is temporary.
    """

    senslist = []
    clock_edge = None
    clock_name = None
    clock_bit = None
    reset_edge = None
    reset_name = None
    reset_bit = None

    for l in node.sens_list.list:
        if l.sig is None:
            continue
        if isinstance(l.sig, Pointer):
            signame = self._get_signal_name(l.sig.var)
            bit = int(l.sig.ptr.value)
        else:
            signame = self._get_signal_name(l.sig)
            bit = 0
##            if signaltype.isClock(signame):
##                clock_name = self.searchTerminal(signame, scope)
##                clock_edge = l.type
##                declared_lsb = self.dataflow.terms[clock_name].lsb.eval()
##                clock_bit = bit - declared_lsb
##            elif signaltype.isReset(signame):
##                reset_name = self.searchTerminal(signame, scope)
##                reset_edge = l.type
##                declared_lsb = self.dataflow.terms[reset_name].lsb.eval()
##                reset_bit = bit - declared_lsb
##            else:
##                senslist.append(l)
        try:
            if self._is_reset(node, l.sig, l.type):
                reset_name = self.searchTerminal(signame, scope)
                reset_edge = l.type
                declared_lsb = self.dataflow.terms[reset_name].lsb.eval()
                reset_bit = bit - declared_lsb
            else:
                clock_name = self.searchTerminal(signame, scope)
                clock_edge = l.type
                declared_lsb = self.dataflow.terms[clock_name].lsb.eval()
                clock_bit = bit - declared_lsb
        except KeyError:
            sys.exit("Error!: " + signame + " isn't declared @" + str(scope) + ".")

    if clock_edge is not None and len(senslist) > 0:
        raise verror.FormatError('Illegal sensitivity list')
    if reset_edge is not None and len(senslist) > 0:
        raise verror.FormatError('Illegal sensitivity list')

    return (clock_name, clock_edge, clock_bit, reset_name, reset_edge, reset_bit,senslist)

def _is_reset(self, node, sig, edge):
    """ [FUNCTIONS]
    This function is assigned as BindVisitor._is_reset (in bindvisitor.py) in pyverilog_toolbox.
    But this correspondence is temporary.
    """
    if not isinstance(node.statement.statements[0], IfStatement):
        return False
    if isinstance(node.statement.statements[0].cond, Ulnot) and edge == 'negedge':
        target = node.statement.statements[0].cond.children()[0]
    elif edge == 'posedge':
        target = node.statement.statements[0].cond
    else:
        return False

    if isinstance(target, pyverilog.vparser.ast.Pointer):
        if sig.ptr == target.ptr:
            target = target.var
        else:
            return False

    return target == sig

class dataflow_facade(VerilogControlflowAnalyzer):
    """ [CLASSES]
        Facade pattern for getting dataflow.
        You can get dataflow by dataflow_facade(Verilog file name).
        If commandline option exists, first argument is regard as verilog file name.
    """
    def __init__(self, code_file_name, topmodule='', config_file=None):
        #TODO this corrspondence is temporal.
        BindVisitor._createAlwaysinfo = _createAlwaysinfo.__get__(BindVisitor)
        BindVisitor._is_reset = _is_reset.__get__(BindVisitor)
        #
        (topmodule, terms, binddict, resolved_terms, resolved_binddict,
         constlist, fsm_vars) = self.get_dataflow(code_file_name)

        VerilogControlflowAnalyzer.__init__(self, topmodule, terms, binddict,
        resolved_terms, resolved_binddict, constlist, fsm_vars)
        self.binds = BindLibrary(binddict, terms)

    def get_dataflow(self, code_file_name, topmodule='', config_file=None):
        optparser = OptionParser()
        optparser.add_option("-t","--top",dest="topmodule",
                             default="TOP", help="Top module, Default=TOP")

        optparser.add_option("-I","--include", dest="include", action="append",
                             default=[],help="Include path")
        optparser.add_option("-D",dest="define", action="append",
                             default=[], help="Macro Definition")
        optparser.add_option("-S", dest="config_file", default=[], help="config_file")
        optparser.add_option("-s", "--search", dest="searchtarget", action="append",
                             default=[], help="Search Target Signal")

        (options, args) = optparser.parse_args()

        if args:
            filelist = args
        elif code_file_name:
            if hasattr(code_file_name, "__iter__") and not isinstance(code_file_name, str):
                filelist = code_file_name
            else:
                filelist = (code_file_name,)
        else:
            raise Exception("Verilog file is not assigned.")

        for f in filelist:
            if not os.path.exists(f): raise IOError("file not found: " + f)

        if not topmodule:
            topmodule = options.topmodule

        analyzer = VerilogDataflowAnalyzer(filelist, topmodule,
                                           preprocess_include=options.include,
                                           preprocess_define=options.define)
        analyzer.generate()

        directives = analyzer.get_directives()
        terms = analyzer.getTerms()
        binddict = analyzer.getBinddict()

        optimizer = VerilogDataflowOptimizer(terms, binddict)

        optimizer.resolveConstant()
        resolved_terms = optimizer.getResolvedTerms()
        resolved_binddict = optimizer.getResolvedBinddict()
        constlist = optimizer.getConstlist()
        if config_file:
            self.config_file = config_file
        elif options.config_file:
            self.config_file = options.config_file

        fsm_vars = (['fsm', 'state', 'count', 'cnt', 'step', 'mode'] + options.searchtarget)
        return options.topmodule, terms, binddict, resolved_terms, resolved_binddict, constlist, fsm_vars

    def make_term_ref_dict(self):
        self.term_ref_dict = {}
        for tv,tk,bvi,bit,term_lsb in self.binds.walk_reg_each_bit():
            if 'Rename' in tv.termtype: continue
            target_tree = self.makeTree(tk)
            tree_list = self.binds.extract_all_dfxxx(target_tree, set([]), bit - term_lsb, DFTerminal)
            for tree, bit in tree_list:
                if str(tree) not in self.term_ref_dict.keys():
                    self.term_ref_dict[str(tree)] = set([])
                self.term_ref_dict[str(tree)].add(str(tk))

    def make_extract_dfterm_dict(self):
        return_dict = {}
        binds = BindLibrary(self.resolved_binddict, self.resolved_terms)
        for tv, tk, bvi, bit, term_lsb in binds.walk_reg_each_bit():
            tree = self.makeTree(tk)
            trees = binds.extract_all_dfxxx(tree, set([]), bit - term_lsb, DFTerminal)
            return_dict[(str(tk), bit)] = set([str(tree) for tree in trees])
        return return_dict

    def decorate_html(html_name):
        temp_html = open('temp.html', 'r')
        out_html = open(html_name, 'w')
        for line in temp_html:
            if 'Term:\n' in line:
                out_html.write('<font size="5">' + line + '</font>' + '<br>')
            elif 'Bind:\n' in line:
                out_html.write('<Hr Color="#fe81df">' + '<font size="5">' + line + '</font>' + '<br>')
            else:
                out_html.write(line + '<br>')
        temp_html.close()
        out_html.close()

    @out_as_html(decorate_html)
    def print_dataflow(self):
        """[FUNCTIONS]
        print dataflow information.
        Compatible with Pyverilog. (Mainly used in gui_main.py)
        """
        terms = self.binds._terms
        print('Term:')
        for tk, tv in sorted(terms.items(), key=lambda x: len(x[0])):
            print(tv.tostr())

        binddict = self.binds._binddict
        print('Bind:')
        for bk, bv in sorted(binddict.items(), key=lambda x: len(x[0])):
            for bvi in bv:
                print(bvi.tostr())

    @out_as_html(decorate_html)
    def print_controlflow(self):
        """[FUNCTIONS]
        print controlflow information.
        Compatible with Pyverilog. (Mainly used in gui_main.py)
        """
        fsms = self.getFiniteStateMachines()

        for signame, fsm in fsms.items():
            print('# SIGNAL NAME: %s' % signame)
            print('# DELAY CNT: %d' % fsm.delaycnt)
            fsm.view()
            if not options.nograph:
                fsm.tograph(filename=util.toFlatname(signame)+'.'+options.graphformat, nolabel=options.nolabel)
            loops = fsm.get_loop()
            print('Loop')
            for loop in loops:
                print(loop)

if __name__ == '__main__':
    df = dataflow_facade("../testcode/complex_partselect.v")
    df.html_name='log.html'
    df.print_dataflow()
    #df.print_controlflow()
