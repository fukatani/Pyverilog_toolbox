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
import pyverilog
from types import MethodType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )



class sample(object):
    def output(self):
        print 'aaaa'

def output_custom(self):
    print 'bbbb'

if __name__ == '__main__':
    s1 = sample()
    s1.output()
    sample.output = MethodType(output_custom, None, sample)
    s1.output()
