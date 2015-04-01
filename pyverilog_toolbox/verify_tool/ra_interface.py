#-------------------------------------------------------------------------------
# ra_interface.py
#
# interface of register map analyzer
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------


import sys
import os
import pyverilog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from regmap_analyzer import *
import pyverilog.controlflow.controlflow_analyzer as controlflow_analyzer


def analize_regmap(code_file_name="",setup_file=""):
    from optparse import OptionParser
    import pyverilog.utils.util as util
    from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
    from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer

    optparser = OptionParser()
    optparser.add_option("-t","--top",dest="topmodule",
                         default="TOP",help="Top module, Default=TOP")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    optparser.add_option("-S",dest="regmap_config",
                         default=[],help="regmap config")

    (options, args) = optparser.parse_args()
    if args:
        filelist = args
    else:
        filelist = {code_file_name}

    if options.regmap_config:
        setup_file = options.regmap_config

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    analyzer = VerilogDataflowAnalyzer(filelist, options.topmodule,
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


    canalyzer = RegMapAnalyzer(options.topmodule, terms, binddict,
                                           resolved_terms, resolved_binddict, constlist, fsm_vars={'reg','r_'})
    map_factory = MapFactory(setup_file)
    write_map, read_map = canalyzer.getRegMaps(map_factory)

    print 'Write_map:\n' + str(write_map.map)
    print 'Read_map:\n' + str(read_map.map)
    return write_map, read_map

if __name__ == '__main__':
    #analize_regmap("../testcode/regmap.v", "../testcode/setup.txt")
    analize_regmap("../testcode/regmap_split.v", "../testcode/setup.txt")