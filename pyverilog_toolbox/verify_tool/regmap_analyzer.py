#-------------------------------------------------------------------------------
# regmap_analyzer.py
#
# Register map analyzer
#
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------

import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyverilog.dataflow.dataflow import *
from pyverilog_toolbox.verify_tool.dataflow_facade import dataflow_facade, out_as_html

import pyverilog.controlflow.splitter as splitter


class RegMapAnalyzer(dataflow_facade):

    def __init__(self, code_file_name, setup_file, topmodule='', out_file='out.csv'):
        dataflow_facade.__init__(self, code_file_name, topmodule=topmodule)
        self.out_file_name = out_file

        if hasattr(self, 'config_file'):
            setup_file = self.config_file
        self.reg_control = MapFactory(setup_file)

    def getRegMaps(self):
        write_map = self.reg_control.create_map('write')
        read_map = self.reg_control.create_map('read')

        for tv, tk, bvi, bit, term_lsb in self.binds.walk_reg_each_bit():
            target_tree = self.makeTree(tk)
            funcdict = splitter.split(target_tree)
            funcdict = splitter.remove_reset_condition(funcdict)
            trees = self.binds.extract_all_dfxxx(target_tree, set([]), bit - term_lsb, DFTerminal)
            write_map.check_new_reg(str(tv), term_lsb, trees, funcdict, bit)
            read_map.check_new_reg(str(tv), term_lsb, trees, funcdict, bit)
        self.out_file = open(self.out_file_name, "w")
        write_map.output_csv(self.out_file)
        read_map.output_csv(self.out_file)
        self.out_file.close()

        print('Write_map:\n' + str(write_map.map))
        print('Read_map:\n' + str(read_map.map))
        return write_map, read_map

    def csv2html(self, csv_file_name):
        """ [FUNCTIONS]
           Convert csv file to html.
           Cited from
           http://www.ctroms.com/blog/code/python/2011/04/20/csv-to-html-table-with-python/
           (by Chris Trombley)
        """
        reader = csv.reader(open(csv_file_name))
        htmlfile = open('log.html', 'w')
        rownum = 0

        htmlfile.write('<table rules="all">')
        for row in reader:
            if rownum == 0:
                htmlfile.write('<tr>')
                for column in row:
                    htmlfile.write('<th>' + column + '</th>')
                htmlfile.write('</tr>')
            else:
                htmlfile.write('<tr>')
                for column in row:
                    htmlfile.write('<td>' + column + '</td>')
                htmlfile.write('</tr>')
            rownum += 1
        htmlfile.write('</table>')

class MapFactory(object):
    def __init__(self, file_name):
        write_flag, read_flag, address, write_data, read_data = self._read_setup_file(file_name)
        self.write_flag = write_flag
        self.read_flag = read_flag
        self.address = address
        self.write_data = write_data
        self.read_data = read_data
    def create_map(self, element):
        if element == 'write':
            return WriteMap(self.write_flag, self.address, self.write_data)
        elif element == 'read':
            return ReadMap(self.read_flag, self.address, self.read_data)
    def _read_setup_file(self, file_name):
        """ [FUNCTIONS]
        define write_flag, read_flag, write_data, address, read_data for regmap_analyzer.
        """
        try:
            setup_file = open(file_name, "r")
            for readline in setup_file:
                if readline[0] == '#': continue
                word_list = readline.split(':')
                if len(word_list) == 2:
                    if word_list[0] == 'WRITE_FLAG':
                        write_flag = word_list[1].replace('\n', '')
                    elif word_list[0] == 'READ_FLAG':
                        read_flag = word_list[1].replace('\n', '')
                    elif word_list[0] == 'ADDRESS':
                        address = word_list[1].replace('\n', '')
                    elif word_list[0] == 'READ_DATA':
                        read_data = word_list[1].replace('\n', '')
                    elif word_list[0] == 'WRITE_DATA':
                        write_data = word_list[1].replace('\n', '')
            setup_file.close()
            return write_flag, read_flag, address, write_data, read_data

        except IOError:
            print(file_name + " can't open for read.")
            return

class WriteMap(object):

    def __init__(self, flag, address, data):
        self.flag = flag
        self.address = address
        self.data = data
        if flag == 'None':
            self.finger_print_signals = set([address, data])
        else:
            self.finger_print_signals = set([flag, address, data])
        self.map = {}
        self.this_map_name = '\nWrite Map\n'

    def output_csv(self, file_handle):
        file_handle.write(self.this_map_name)
        self.calc_map_spec()
        file_handle.write('ADD,')
        for i in range(self.max_bit - 1, -1, -1):
            file_handle.write(str(i) + ',')
        for address, reg in sorted(self.map.items(), key=lambda x: x[0]):
            file_handle.write('\n')
            file_handle.write(str(address) + ',')
            for i in range(self.max_bit - 1, -1, -1):
                if i in reg.keys():
                    signal = reg[i]
                    file_handle.write(signal[0] + '[' + str(signal[1]) + ']' + ',')
                else:
                    file_handle.write(',')

    def calc_map_spec(self):
        max_bit = 0
        for address, reg in self.map.items():
            if max(reg.keys()) > max_bit:
                max_bit = max(reg.keys())
        self.max_bit = max_bit + 1
        if self.map:
            self.max_address = max(self.map.keys())

    def _add_new_reg(self, sig_name, sig_bit, address, map_bit):
        if address not in self.map.keys():
            self.map[address] = {}
        if map_bit not in self.map[address]:
            self.map[address][map_bit] = (sig_name, sig_bit)
        else:
            assert self.map[address][map_bit][0] == sig_name, 'duplicated address is exist @ADR:' + str(address)

    def get_map_info(self, trees, funcdict):
        for tree in trees:
            sig_name = str(tree[0])
            if sig_name == self.data:
                bit = tree[1]
        address, map_lsb = self.get_address(funcdict)
        return address, bit

    def get_address(self, funcdict):
        return_val = -1
        for key, verb in funcdict.items():
            if isinstance(verb, DFPartselect):
                signal = str(verb.var)
                map_lsb = verb.lsb.value
            else:
                signal = str(verb)
                map_lsb = 0
            if signal == self.data:
                if return_val == -1:
                    return_val = key[-1].nextnodes[1].value
                else:
                    assert return_val == key[-1].nextnodes[1].value
        return return_val, map_lsb

    def check_new_reg(self, reg_name, term_lsb, trees, funcdict, map_bit):
        sig_names = set([str(tree[0]) for tree in trees])
        if self.finger_print_signals.issubset(sig_names):
            address, bit = self.get_map_info(trees, funcdict)
            if address != -1:
                self._add_new_reg(reg_name, map_bit, address, bit)

class ReadMap(WriteMap):
    def __init__(self, flag, address, data):
        WriteMap.__init__(self, flag, address, data)
        self.this_map_name = '\nRead Map\n'

    def check_new_reg(self, reg_name, term_lsb, trees, funcdict, map_bit):
        sig_names = set([str(tree[0]) for tree in trees]) | set([reg_name])
        if self.finger_print_signals.issubset(sig_names):
            self.get_map_info(trees, funcdict, map_bit)

    def get_map_info(self, trees, funcdict, map_bit):
        def is_data_sig(sig_name, verb):
            if isinstance(verb, DFPartselect):
                return sig_name == str(verb.var)
            elif hasattr(verb, 'nextnodes'):
                return sig_name in str(verb.nextnodes)
            else:
                return sig_name == str(verb)

        for key, verb in funcdict.items():
            for ope in key:
                nextnodes_str = [str(nextnode) for nextnode in ope.nextnodes]
                if str(ope) == 'Eq' and self.address in nextnodes_str:
                    address = ope.nextnodes[1].value if str(ope.nextnodes[0]) == self.address else ope.nextnodes[0].value
            for tree in trees:
                sig_name = str(tree[0])
                sig_bit = tree[1]
                if is_data_sig(sig_name, verb):
                    self._add_new_reg(sig_name, sig_bit, address, map_bit)


if __name__ == '__main__':
    ranalyzer = RegMapAnalyzer("../testcode/regmap_split.v", "../testcode/setup.txt")
    ranalyzer.getRegMaps()
