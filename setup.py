from setuptools import setup, find_packages

import io
import os
import re

version = '0.0.6'

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def read(filename):
    return io.open(os.path.join(CURRENT_DIR, filename), encoding='utf-8').read()

setup(name='pyverilog_toolbox',
      version=version,
      description='Pyverilog-based verification/design tools',
      keywords = 'Verilog, Register Map, code clone, code metrics',
      author='Ryosuke Fukatani',
      author_email='nannyakannya@gmail.com',
      url='https://github.com/fukatani/Pyverilog_toolbox',
      license="Apache License 2.0",
      packages=find_packages(),
      package_data={ 'pyverilog_toolbox' : ['testcode/*'], },
      long_description=read('Readme.rst'),
)

