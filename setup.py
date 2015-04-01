from setuptools import setup, find_packages

import re
import os

version = '0.0.0'

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(name='pyverilog_tool_box',
      version=version,
      description='Pyverilog-based verification/design tools',
      keywords = 'Verilog HDL, Register Map',
      author='Ryosuke Fukatani',
      license="Apache License 2.0",
      packages=find_packages(),
      package_data={ 'pyverilog_toolbox' : ['testcode/*'], },
)

