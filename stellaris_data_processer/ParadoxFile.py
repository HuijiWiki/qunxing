import json
import os
import re
from collections import OrderedDict

from utilities import hsv2rgb, rgb_hex

signals = ['<=', '>=', '<', '>']


class ParadoxFile:
    def __init__(self, path='', filename='', unprocessed=None):
        if unprocessed is None:
            unprocessed = []
        self.unprocessed = unprocessed
        self.path = path
        self.filename = filename
        self.data = OrderedDict()
        self.empty = OrderedDict()
        self.raw_data = ''
        self.iterator = -1
        self.lines = []
        self.length = 0
        self.file_type = ''
        self.level = 0
        self.levels = []
        self.listed_data = False
        name_struct = filename.split('.')
        if len(name_struct) > 0:
            self.file_type = name_struct[-1]

    def open(self):
        try:
            with open(os.path.join(self.path, self.filename), 'r', encoding='UTF-8') as f:
                self.raw_data = f.read()
        except UnicodeDecodeError:
            with open(os.path.join(self.path, self.filename), 'r', encoding='ISO-8859-1') as f:
                self.raw_data = f.read()

    def process(self):
        file_types = {
            'yml': self._read_yml,
            'csv': self._read_csv,
            'txt': self._read_txt,
            'json': self._read_json,
            'gfx': self._read_txt,
        }
        self.open()
        try:
            file_types[self.file_type]()
        except KeyError:
            self.unprocessed.append(os.path.join(self.path, self.filename))

    def get_data(self):
        self.process()
        return self.data

    # readers
    def _read_yml(self):
        lines = self.raw_data.split('\n')
        for i in range(len(lines)):
            refined_one = re.sub(r'(^\s*#.*)', r'', lines[i])
            refined_one = refined_one.replace('$NAME$', '$has_a$')
            one_loc = re.findall(r'^\s*(.*?):\s*\d*\s*"(.*)"', refined_one)
            if len(one_loc) == 0:
                if self.filename not in self.empty:
                    self.empty[self.filename] = OrderedDict()
                self.empty[self.filename][i] = lines[i]
            elif len(one_loc) > 1:
                z = 9
            else:
                if one_loc[0][0] in self.data:
                    z = 8
                self.data[one_loc[0][0]] = one_loc[0][1]

    def _read_csv(self):
        data = re.sub(r'(#.*?)\n', r'\n', self.raw_data)
        data = re.sub(r'(#[^\n]*?)$', r'', data)
        data = re.sub(r'\n+', r'\n', data)
        data = re.sub(r'^\n+', r'', data)
        keys = []
        self.lines = data.split('\n')
        for i in range(len(self.lines)):
            cols = self.lines[i].split(';')
            if i == 0:
                keys = cols
            else:
                for j in range(len(cols) - 1):
                    if j == 0:
                        self.data[cols[0]] = OrderedDict()
                    else:
                        self.data[cols[0]][keys[j]] = cols[j]
        z = 7

    def _read_json(self):
        self.data = json.loads(self.raw_data)

    def _read_txt(self):
        # 去掉注释、去掉对齐用的tab、大括号换行
        data = re.sub(r'(#.*?)\n', r'\n', self.raw_data)
        data = re.sub(r'(#[^\n]*?)$', r'', data)
        data = re.sub(r'hsv\s*{\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*?)\s*}', hsv2rgb, data)
        data = re.sub(r'rgb\s*{\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*?)\s*}', rgb_hex, data)
        data = re.sub(r'\n\s+', r'\n', data)
        data = re.sub(r'\s+\n', r'\n', data)
        data = re.sub(r'{\s', r'{\n', data)
        data = re.sub(r'\s}', r'\n}', data)
        data = re.sub(r'(\S)}', r'\1\n}', data)
        data = re.sub(r'}([^\n])', r'}\n\1', data)
        data = re.sub(r' +', r' ', data)
        data = re.sub(r'=\s*\n+\s*{', r'= {', data)
        data = re.sub(r'option {', r'option = {', data)
        data = re.sub(r'if {', r'if = {', data)
        data = re.sub(r'trigger {', r'trigger = {', data)
        for i in range(len(signals)):
            data = re.sub(r'([^ \n]+ ' + signals[i] + r' [^ "\n]+) ', r'\n\1\n', data)
            # Paradox switch
            data = re.sub(r'\n(.*?) ' + signals[i] + r' {\n', r'\ncase ' + signals[i] + r' \1 = {\n', data)
        data = re.sub(r'[\t ]*=[\t ]*', r' = ', data)
        data = re.sub(r'\n\s*\n', r'\n', data)
        data = data.replace('> =', '>＝').replace('< =', '<＝').replace('>', '= >').replace('<', '= <')
        data = re.sub(r'(\S+ = \S+) (\S+ = \S+)', r'\1\n\2', data)

        find_diff = re.findall(r'[^\s]{', data)
        if len(find_diff) > 0:
            z = 5
        find_diff = re.findall(r'[^=] {', data)
        if len(find_diff) > 0:
            z = 4

        # 嗯个，处理
        self.lines = data.split('\n')
        self.length = len(self.lines)
        self.iterator = -1

        while self.iterator < self.length - 1:
            loop_data = self.process_loop()
            self.merge(loop_data)
        z = 1

    def merge(self, loop_data):
        if len(self.data) == 0:
            self.data = loop_data
        elif len(self.data) == 1:
            for name in self.data:
                for loop_name in loop_data:
                    if name == loop_name:
                        self.data = [self.data]
                        self.data.append(loop_data)
                        self.listed_data = True
        elif self.listed_data:
            self.data.append(loop_data)
        else:
            self.data.update(loop_data)

    def process_loop(self):
        data = OrderedDict()
        list_data = []
        level = 0
        while self.iterator < self.length - 1:
            self.iterator += 1
            new_str = self.lines[self.iterator]
            find_line = re.findall(r'^(.*?)\s*=\s*(.*?)$', new_str)
            if self.lines[self.iterator] == '}':
                self.level -= 1
                break
            elif len(find_line) > 0:
                data_line = find_line[0]
                if data_line[1] == '{':
                    self.levels.append(data_line[0])
                    level += 1
                    self.level += 1
                    temp_data = self.process_loop()
                else:
                    temp_data = data_line[1].replace('＝', '=')
                if data_line[0] in data:
                    if type(data[data_line[0]]) != list:
                        data[data_line[0]] = [data[data_line[0]]]
                    data[data_line[0]].append(temp_data)
                else:
                    data[data_line[0]] = temp_data
            elif self.lines[self.iterator] == '{':
                self.level += 1
            elif self.lines[self.iterator] != '':
                list_data.append(self.lines[self.iterator])
                if len(data) > 0:
                    z = 3
            if level == -1:
                break
        if len(list_data) > 0:
            if len(data) > 0:
                z = 2
            data = list_data
        return data
