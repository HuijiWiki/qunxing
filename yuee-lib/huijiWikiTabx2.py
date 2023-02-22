# 处理和维护HuijiWiki中Tabx类数据的模块
import json
from collections import OrderedDict
from danteng_lib import log
from danteng_excel import read_sheet_from_xlsx
from SaveToExcel import save_to_excel
import os


# wiki：用于操作的huijiWiki对象
# title：存储Tabx的数据所在页面名称
# key：默认为''，如果不为空字符串的话，将使用header中的这个项目当作key来生成数据
class HuijiWikiTabx(object):
    def __init__(self, wiki):
        self._wiki = wiki
        self._title = ''  # 当前使用的title
        self._tabx_text = OrderedDict()   # TABX数据字典
        self._header = []  # 数据的表头
        self._data = []  # 列表数据

        self._ready = False

        # 如果使用KEY模式的时候会用到
        self._key = ''  # 当作key的header，该列数据需要值唯一
        self._key_data = OrderedDict()  # 数据字典

    # 创建一个新的表
    def create_new_tabx(self):
        self._tabx_text = OrderedDict([
            ('license', 'CC0-1.0'),
            ('description', OrderedDict([
                ('en', 'table description'),
            ])),
            ('sources', 'Create by huijiWikiTabx'),
            ('schema', OrderedDict([
                ('fields', [])
            ])),
            ('data', [])
        ])
        self.generate_header(True)
        self.generate_data(True)
        self._ready = True
        return True

    # 读取线上一个页面的数据到本地
    def load(self, title, key=''):
        self._wiki.raw(title, notice=False)
        self._wiki.wait_threads()
        result = self._wiki.get_result()
        if len(result) == 1:
            self._tabx_text = json.loads(result[0]['rawtext'], object_pairs_hook=OrderedDict)
            self._title = title
            if key != '':
                self._key = key
            self.generate_header()
            self.generate_data()

            return True
        else:
            return False

    # 判断数据是否准备就绪
    def is_ready(self):
        return self._ready

    # 生成表头
    def generate_header(self, is_new=False):
        # 获取header
        self._header = []
        if is_new:
            return True
        if 'schema' not in self._tabx_text:
            log('[[%s]]数据有误：未找到表头字段，请检查。' % self._title)
            return False
        if 'fields' not in self._tabx_text['schema']:
            log('[[%s]]数据有误：未找到表头字段，请检查。' % self._title)
            return False
        for field in self._tabx_text['schema']['fields']:
            self._header.append(field['title']['en'])
        if self._key != '' and self._key not in self._header:
            log('[[%s]]数据有误：表头字段中未找到当作KEY的“%s”，请检查。' % (self._title, self._key))
            return False
        return True

    # 获取表头
    def get_header(self):
        return self._header

    # 获取原始表头
    def get_original_header(self):
        return self._tabx_text['schema']['fields']

    # 设置原始表头
    def set_original_header(self, header):
        self._tabx_text['schema']['fields'] = header
        self.generate_header()

    # 生成数据
    def generate_data(self, is_new=False):
        self._data = []
        self._key_data = OrderedDict()
        if is_new:
            return True
        if 'data' not in self._tabx_text:
            log('[[%s]]数据有误：未找到内容数据，请检查。' % self._title)
            return False
        for index in range(0, len(self._tabx_text['data'])):
            row_data = OrderedDict()
            for key_index in range(0, len(self._header)):
                row_data[self._header[key_index]] = self._tabx_text['data'][index][key_index]
            self._data.append(row_data)

            if self._key != '':
                if self._key not in row_data:
                    raise Exception('行数据中没有名为 %s 的key' % self._key)
                self._key_data[row_data[self._key]] = row_data
        return True

    # 获取全部数据
    def get_all_data(self):
        return self._data

    # 获取全部数据
    def get_all_key_data(self):
        return self._key_data

    # 获取数据长度
    def length(self):
        return len(self._data)

    # 查询是否有key模式的数据
    def has_key_data(self):
        return self._key != ''

    # 【key数据】查询中是否有某个key
    def has_row(self, key):
        return key in self._key_data

    # 【key数据】获取指定key的row_data
    def get_row(self, key):
        if key in self._data:
            return self._key_data[key]
        else:
            return False

    # 【key数据】添加/修改新的行
    def mod_row(self, key, new_data):
        temp_data = OrderedDict()
        for key_index in range(0, len(self._header)):
            header_name = self._header[key_index]
            if header_name == self._key:
                temp_data[header_name] = key
            elif header_name in new_data:
                temp_data[header_name] = new_data[header_name]
            else:
                temp_data[header_name] = None
        self._data[key] = temp_data

    # 保存回服务器
    def save(self, title='', wikitext_path=None):
        if len(self._header) == 0:
            return False
        if title != '':
            self._title = title

        new_data = []
        for row_data in self._data.values():
            temp_row = []
            for key_name in self._header:
                if row_data[key_name] == '':
                    temp_row.append(None)
                else:
                    temp_row.append(row_data[key_name])
            new_data.append(temp_row)
        self._tabx_text['data'] = new_data

        if wikitext_path:
            filepath = os.path.join(wikitext_path, self._wiki.filename_fix('%s.txt' % self._title))
            self._wiki.edit(self._title, json.dumps(self._tabx_text, ensure_ascii=False), filepath=filepath,
                            compare_flag=True)
        else:
            self._wiki.edit(self._title, json.dumps(self._tabx_text, ensure_ascii=False))

        return True

    # 打开一个excel
    def open_xlsx(self, xlsx_path):
        xlsx_data = read_sheet_from_xlsx(xlsx_path, sheet_index=0, mode='simple')
        xlsx_data = xlsx_data[list(xlsx_data.keys())[0]]

        new_data = OrderedDict([
            ('license', 'CC0-1.0'),
            ('description', OrderedDict([
                ('en', '请输入简要描述')
            ])),
            ('sources', '导入自 %s by Bot' % os.path.split(xlsx_path)[1]),
            ('schema', OrderedDict([
                ('fields', []),
            ])),
            ('data', [])
        ])

        # 首先把A1放进header
        ex_data_key = list(xlsx_data['data'].keys())[0]
        ex_data = xlsx_data['data'][ex_data_key]

        new_data['schema']['fields'].append(OrderedDict([
            ('name', self.get_header_name(xlsx_data['a1'])),
            ('type', self.get_value_type(ex_data_key)),
            ('title', OrderedDict([
                ('en', xlsx_data['a1'])
            ]))
        ]))

        # 把其他表头放进去
        for header in xlsx_data['header']:
            new_data['schema']['fields'].append(OrderedDict([
                ('name', self.get_header_name(header)),
                ('type', self.get_value_type(ex_data[header])),
                ('title', OrderedDict([
                    ('en', header)
                ]))
            ]))

        for data_key, info in xlsx_data['data'].items():
            temp_data = [data_key]
            for header in xlsx_data['header']:
                temp_data.append(info[header])
            new_data['data'].append(temp_data)

        self._tabx_text = new_data
        return self.generate_header() and self.generate_data()

    @staticmethod
    def get_value_type(value):
        value_type = type(value)
        value_type_text = 'string'
        if value_type in [int, float]:
            value_type_text = 'number'
        elif value_type == bool:
            value_type_text = 'boolean'
        return value_type_text

    @staticmethod
    def get_header_name(header):
        output = header
        if len(header) >= 2 and output[-2:] == '[]':
            output = output[:-2]
        return output

    # 保存为xlsx
    def save_as_xlsx(self, xlsx_path, save_sheet_name):
        # 生成excel数据
        headers = OrderedDict([
            (save_sheet_name, [])
        ])
        contents = OrderedDict([
            (save_sheet_name, OrderedDict())
        ])

        for item_key, info in self._data.items():
            for key, vaule in info.items():
                if key not in headers[save_sheet_name]:
                    headers[save_sheet_name].append(key)
                if item_key not in contents[save_sheet_name]:
                    contents[save_sheet_name][item_key] = {}
                if vaule == None:
                    contents[save_sheet_name][item_key][key] = ''
                else:
                    contents[save_sheet_name][item_key][key] = vaule

        save_to_excel(headers, contents, xlsx_path)
        return True

    # 从一个list导入数据
    # list中每个项目是一个dict
    # 每个header的类型由第一次出现时的属性决定
    def import_from_list(self, data_list, sources=''):
        new_data = OrderedDict([
            ('license', 'CC0-1.0'),
            ('description', OrderedDict([
                ('en', '请输入简要描述')
            ])),
            ('sources', sources),
            ('schema', OrderedDict([
                ('fields', []),
            ])),
            ('data', [])
        ])

        # 记录已经有哪些header了
        already_header = []

        # 整理数据（list转成字符串），并且梳理出header
        for data_content in data_list:
            for header in list(data_content.keys()):
                header_name = header
                value = data_content[header]
                if type(value) == list:
                    header_name = '%s[]' % header
                    value = ';'.join(value)
                    data_content[header_name] = value
                if header_name not in already_header:
                    new_data['schema']['fields'].append(OrderedDict([
                        ('name', header_name),
                        ('type', self.get_value_type(value)),
                        ('title', OrderedDict([
                            ('en', header)
                        ]))
                    ]))

                    already_header.append(header_name)

        for data_content in data_list:
            temp_data = []
            for header in already_header:
                temp_data.append(data_content[header])
            new_data['data'].append(temp_data)

        self._tabx_text = new_data
        return self.generate_header() and self.generate_data()
