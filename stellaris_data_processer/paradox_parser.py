import os
from collections import OrderedDict
import re

from danteng import Danteng

# 读取规则文件(*.txt)和本地化文件(*.yml)
# 这里只读取不处理
from utilities import hsv2rgb


class ParadoxParser(object):
    file_path = ''
    file_text = ''
    global_var = None
    key_dict = OrderedDict()
    data = OrderedDict()
    error = False
    error_msg = ''
    mode = ''
    main_category = ''

    def __init__(self, file_path='', item_category='none'):
        self.main_category = item_category[0:-1]
        if file_path != '':
            self.open(file_path)

    def init(self):
        self.file_path = ''
        self.file_text = ''
        self.global_var = OrderedDict()
        self.key_dict = OrderedDict()
        self.data = OrderedDict()
        self.error = False
        self.error_msg = ''
        self.mode = ''

    # 打开一个文件
    def open(self, file_path):
        if file_path[-4:] == '.txt' or file_path[-4:] == '.gfx':
            self.mode = 'txt'
            return self.open_txt(file_path)
        elif file_path[-4:] == '.yml':
            self.mode = 'yml'
            return self.open_yml(file_path)
        elif file_path[-4:] == '.csv':
            self.mode = 'csv'
            return self.open_csv(file_path)
        else:
            Danteng.log('%s' % file_path)

    # 打开文本文件（配置文件）
    def open_txt(self, file_path):
        self.init()
        if os.path.exists(file_path):
            self.file_path = file_path
            with open(self.file_path, 'r', encoding='UTF-8') as f:
                self.file_text = f.read()

            # 如果有HSV颜色的话，比如atmosphere_color = hsv { 0.50 0.2 0.8 }
            self.file_text = re.sub(r'hsv\s*{\s*(.+?\s+.+?\s+.+?)\s*}', hsv2rgb, self.file_text)
            self.file_text = re.sub(r'#.*?\n', '\n', self.file_text)
            self.file_text = re.sub(r'{(\s*min\s*=\s*.+?)(\smax\s*=\s*.+?\s*)}', r'{\1\n\2}', self.file_text)
            # 把非标准换行替换成标准换行'modifiers = {\n'，'}'前换行
            self.file_text = re.sub(r'\n*\s*=\s*\n*\s*{\s*\n*', ' = {\n', self.file_text)
            self.file_text = re.sub(r'\s*}', '}', self.file_text)
            self.file_text = re.sub(r'(?<!\n)}', '\n}', self.file_text)
            self.file_text = re.sub(r'{(\s*x\s*=\s*.+?)(\sy\s*=\s*.+?\s*)}', r'{\1\n\2}', self.file_text)
            self.file_text = re.sub(r'{(\s*locator\s*=\s*.+?)(\s*locator\s*=\s*.+?\s*)}', r'{\1\n\2}', self.file_text)
            self.file_text = re.sub(r'(\".*?\"\s*=\s*{\s*locator\s*=\s*\".*?\"\s*})', r'\1\n', self.file_text)
            self.file_text = re.sub(r'{(\s*who\s*=\s*.+?)(\smodifier\s*=\s*.+?\s*)}', r'{\1\n\2}', self.file_text)
            self.file_text = re.sub(r'(= \S*?) (\S*? =)', r'\1\n\2', self.file_text)

            # 分析文件的根目录
            root_text_list, self.global_var = self.analyze_one_level(self.file_text)

            # 将每一段内容进行解析
            for root_text in root_text_list:
                temp_title, temp_data = self.analyze_one_item(root_text)
                if 'key' in temp_data:
                    temp_title = '%s_%s' % (self.main_category, temp_data['key'].replace('"', ''))
                elif 'name' in temp_data:
                    temp_data['sub_category'] = temp_title
                    temp_title = '%s_%s' % (self.main_category, temp_data['name'].replace('"', ''))
                elif 'id' in temp_data:
                    temp_data['sub_category'] = temp_title
                    temp_title = '%s_%s' % (self.main_category, temp_data['id'].replace('"', ''))
                elif temp_title == 'terraform_link' and 'from' in temp_data and 'to' in temp_data:
                    temp_data['from'] = temp_data['from'].replace('"', '')
                    temp_data['to'] = temp_data['to'].replace('"', '')
                    temp_title = '%s_%s_%s' % (temp_title, temp_data['from'], temp_data['to'])

                self.data[temp_title] = temp_data

            return True
        else:
            Danteng.log('所要打开的文件不存在')
            return False

    # 获取数据
    def get_data(self):
        # self.data = var_processor(self.data, self.global_var)
        return self.data, self.global_var

    # 获取KEY表
    def get_key_dict(self):
        if self.mode == 'txt':
            if len(self.key_dict) == 0:
                # 查找所有key
                self.find_all_key()

        return self.key_dict

    # 查找所有key
    def find_all_key(self):
        self.key_dict = self.find_key(self.data)

        for key in self.key_dict:
            self.key_dict[key]['name'] = key
            self.key_dict[key]['type'] = ','.join(self.key_dict[key]['type_list'])
            self.key_dict[key]['depth'] = ','.join(self.key_dict[key]['depth_list'])
            self.key_dict[key]['parent'] = ','.join(self.key_dict[key]['parent_list'])

    # 查找所有key
    def find_key(self, data, key_dict=None, parent='', depth=0):
        if type(key_dict) != OrderedDict:
            key_dict = OrderedDict()
        for key in data:
            if parent == '':
                key_dict = self.find_key(data[key], key_dict, 'root', depth + 1)
            else:
                if type(data[key]) == OrderedDict or type(data[key]) == dict:
                    key_type = 'dict'
                elif type(data[key]) == list:
                    key_type = 'list'
                elif type(data[key]) == str:
                    key_type = 'str'
                else:
                    key_type = 'unknown'

                if key not in key_dict:
                    key_dict[key] = {
                        'parent_list': [parent],
                        'type_list': [key_type],
                        'example': str(data[key]),
                        'count': 1,
                        'depth_list': [str(depth)]
                    }
                else:
                    key_dict[key]['count'] += 1
                    if parent not in key_dict[key]['parent_list']:
                        key_dict[key]['parent_list'].append(parent)
                    if key_type not in key_dict[key]['type_list']:
                        key_dict[key]['type_list'].append(key_type)
                    if str(depth) not in key_dict[key]['depth_list']:
                        key_dict[key]['depth_list'].append(str(depth))

                if key_type == 'dict':
                    key_dict = self.find_key(data[key], key_dict, key, depth + 1)

        return key_dict

    # 解析单个项目
    def analyze_one_item(self, text):
        data = OrderedDict()
        remain_text = text
        text_array = text.split('\n')
        # 查找项目标题
        title = re.findall(r'^(.*?)\s*=\s*{$', text_array[0].strip())
        if len(title) == 1:
            title = title[0]
            remain_text = '\n'.join(text_array[1:])
        else:
            title = ''
            print('出现错误！请检查！text：%s' % text[0:20])

        while remain_text != '':
            text_array = remain_text.split('\n')
            temp_title = ''
            temp_data = ''
            found = False
            remain_text_array = []

            cur_text = text_array[0].strip()

            # 第一种类型
            # 子标题型
            # 如：weight_modifier = {
            sub_title = re.findall(r'^(.*?)\s*=\s*{$', cur_text)
            if sub_title:
                sub_text, remain_text_array = self.analyze_one_level('\n'.join(text_array[0:]), 1)
                temp_title, temp_data = self.analyze_one_item(sub_text[0])
                found = True

            # 第二种类型
            # 大于/小于型
            # 如：num_strategic_resources > 9
            if not found:
                find = re.findall(r'^(.*?)\s*([><]\s*.*)$', cur_text)
                if find:
                    temp_title = find[0][0]
                    temp_data = find[0][1]
                    found = True

            # 第三种类型
            # 赋值型
            # 如：weight = 100
            if not found:
                find = re.findall(r'^(.*?)\s*=\s*(.*)$', cur_text)
                if find:
                    temp_title = find[0][0]
                    temp_data = find[0][1]

                    temp_data = self.analyze_one_line(temp_data)
                    found = True

            if found:
                if temp_title in data:
                    if type(data[temp_title]) == list:
                        data[temp_title].append(temp_data)
                    else:
                        temp_list = [data[temp_title]]
                        data[temp_title] = temp_list
                        data[temp_title].append(temp_data)
                else:
                    try:
                        data[temp_title] = temp_data
                    except:
                        x = 1
            else:
                if cur_text in ['{', '}']:
                    pass
                # 第四种类型
                # 没有逻辑运算符的，而且不是'}'
                else:
                    if len(data) == 0:
                        data = [cur_text]
                    else:
                        if type(data) == list:
                            data.append(cur_text)
                        else:
                            Danteng.log('出现错误运算行：%s' % cur_text[0:100])
                            # Danteng.log('无逻辑运算符行：%s' % cur_text[0:100])

            if len(remain_text_array) > 0:
                remain_text = '\n'.join(remain_text_array)
            else:
                if len(text_array) > 0:
                    remain_text = '\n'.join(text_array[1:])
                else:
                    remain_text = ''

        return title, data

    def analyze_one_line(self, text):
        if text == '':
            return text
        if text[0] == '{' and text[-1] == '}':
            find = re.findall(r'^{\s*(.*?)\s*=\s*(.*?)\s*}$', text)
            if find:
                temp_title = find[0][0].strip()
                temp_data = find[0][1].strip()
                if temp_data[0] == '{' and text[-1] == '}':
                    temp_data = self.analyze_one_line(temp_data)
                return {temp_title: temp_data}
            else:
                temp_data = text[1:-1].strip()
                return [temp_data]
        else:
            return text

    # 解析一级
    def analyze_one_level(self, text, count=-1):
        text_list = []  # 返回值存放
        temp_text = ''  # 临时文本存放
        is_in_depth = False  # 处于括号层中
        bracket_depth = 0  # 深度计数器
        count_total = 0  # 查找数量计数器
        remain_text_array = []

        # 占位（全局变量）
        global_var = OrderedDict()

        text_array = text.split('\n')
        for i in range(0, len(text_array)):
            line = text_array[i]
            # 除掉注释
            line = re.sub(r'^([^#]*)#?.*$', r'\1', line)
            line = line.strip()
            # 如果空行则跳过
            if line == '':
                continue

            # 需要+1
            left_count = line.count('{')
            right_count = line.count('}')

            # 如果是全局变量
            if not is_in_depth and line.strip()[0] == '@':
                find = re.findall(r'^(.*?)\s*=\s*(.*)$', line.strip())
                if len(find) == 1:
                    global_var[find[0][0]] = find[0][1]
                else:
                    print('出现错误！请检查！text：' % line.strip()[0:20])
                continue
            elif not is_in_depth and line.find('{') == -1 and line.find('}') == -1:
                find = re.findall(r'^(.*?)\s*([=><]\s*.*)$', line.strip())
                if len(find) == 1:
                    if find[0][1][0] == '=':
                        global_var[find[0][0]] = find[0][1][1:]
                    else:
                        global_var[find[0][0]] = find[0][1]
                else:
                    print('出现错误！请检查！text：%s' % line.strip()[0:20])
                continue
            else:
                if left_count > 0 or right_count > 0:
                    temp_line = line
                    next_pos = 0

                    while next_pos != -1:
                        if temp_line == '{' or temp_line == '}':
                            break
                        elif len(temp_line) > 0 and temp_line[-1] == '{' and temp_line.count('{') == 1:
                            break

                        find_left = temp_line.find('{')
                        find_right = temp_line.find('}')
                        if find_left == -1 and find_right == -1:
                            break
                        elif find_left == -1 or (find_right != -1 and find_right < find_left):
                            next_pos = find_right
                            temp_text += temp_line[0:next_pos].strip() + '\n'
                            temp_text += temp_line[next_pos:(next_pos + 1)].strip() + '\n'
                            temp_line = temp_line[(next_pos + 1):].strip()
                        else:
                            next_pos = find_left
                            temp_text += temp_line[0:(next_pos + 1)].strip() + '\n'
                            temp_line = temp_line[(next_pos + 1):].strip()

                    if temp_line != '':
                        temp_text += temp_line + '\n'

                elif line.find('\t') > -1:
                    find = re.findall(r'^([^\s]+)\s*=\s*(.+)$', line)
                    if find:
                        if find[0][1].find('=') > -1:
                            f1_array = re.findall(r'^(.+)\s([^\s]+)\s*=\s*(.+)$', find[0][1])
                            if f1_array[0][2].find('=') > -1:
                                print('发现第三个=，请检查')
                            temp_text += '%s = %s\n%s = %s\n' % (
                                find[0][0], f1_array[0][0], f1_array[0][1], f1_array[0][2])
                        else:
                            temp_text += '%s = %s\n' % (find[0][0], find[0][1])
                else:
                    temp_text += line + '\n'

            bracket_depth += left_count
            bracket_depth -= right_count
            # 检查三种情况
            # # 第三种，行中间出现 { ，但行内没出现 }
            # if depth_plus > 0:
            #     bracket_depth += depth_plus
            # # 第一种，末尾是 {
            # # 括号深度+1
            # elif line[-1] == '{':
            #     bracket_depth += 1
            # # 第二种，当前行为 }
            # # 括号深度-1
            # elif line == '}':
            #     bracket_depth -= 1

            # 如果在括号深度里，并且当前深度为0
            # 说明结束了一次检测
            if (is_in_depth and bracket_depth == 0) or (
                    not is_in_depth and left_count == 1 and right_count == 1):
                text_list.append(temp_text)
                temp_text = ''
                is_in_depth = False
                count_total += 1
                if count_total == count:
                    if i < len(text_array):
                        remain_text_array = text_array[i + 1:]
                    break
            elif not is_in_depth and bracket_depth > 0:
                is_in_depth = True

        if count == -1:
            return text_list, global_var
        else:
            return text_list, remain_text_array

    # 打开YML文件（本地化文件）
    def open_yml(self, file_path):
        self.init()
        if os.path.exists(file_path):
            self.file_path = file_path
            with open(self.file_path, 'r', encoding='UTF-8') as f:
                self.file_text = f.read()
            # 读取本地化文件
            return self.analyze_yml_text()
        else:
            Danteng.log('所要打开的文件不存在')
            return False

    # 解析YML文件
    def analyze_yml_text(self):
        text_array = self.file_text.split('\n')
        for i in range(0, len(text_array)):
            line = text_array[i].strip()

            # 跳过空行
            if line == '':
                continue

            # 去掉注释
            # find = re.findall(r'^([^#]*)#.*$', line)                          # 瑞典蠢驴的"#"可能出现在字符串内部
            # find = re.findall(r'^\s*[a-z0-9._]+:[0-9]\s*\".*?\"$', line)      # 瑞典蠢驴的"\""可能出现在字符串内部
            if line[0] == '#':  # "#"开头直接是注释行
                continue

            # 查找是否符合条件
            find = re.findall(r'(.*?):\d*?\s*?"(.*)"', line)
            if find and find[0][1] != '':
                self.data[find[0][0]] = find[0][1]
            else:
                if line != '﻿l_english:' and line != '﻿l_english_tag:':
                    Danteng.log('这行没找到任何数据：%s' % line)
        return True

    # 打开csv文件（武器参数列表文件）
    def open_csv(self, file_path):
        self.init()
        if os.path.exists(file_path):
            self.file_path = file_path

            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.file_text = f.read()
            # 读取武器参数文件
            return self.analyze_csv()
        else:
            Danteng.log('所要打开的文件不存在')
            return False

    # 解析YML文件
    def analyze_csv(self):
        self.file_text = re.sub(r'#.*?\n', '\n', self.file_text)
        self.file_text = re.sub(r'\n+', '\n', self.file_text)
        text_array = self.file_text.split('\n')
        title=['key']
        for i in range(0, len(text_array)):
            line = text_array[i].strip()
            if len(line) != 0:
                line_data = re.findall(r'([^;]+)', line)
                raw_data={}
                if line[0:3] == 'key':
                    title = line_data
                else:
                    for j in range(0, len(line_data)):
                        raw_data[title[j]] = line_data[j]
                    self.data[raw_data['key']] = raw_data
        return True
