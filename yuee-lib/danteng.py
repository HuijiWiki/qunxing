#!/usr/bin/python
#  -*- coding:utf-8 -*-

from time import strftime, localtime
import os
import xlrd
import requests
import codecs
import configparser
import re
import csv
import unicodecsv
import pickle
from collections import OrderedDict


__author__ = 'Yuee'


class Danteng(object):
    @staticmethod
    def log(string, error_string=''):
        _str = '%s %s' % (strftime("[%H:%M:%S]", localtime()), string)
        try:
            print('%s %s' % (strftime("[%H:%M:%S]", localtime()), string))
        except:
            print('%s %s' % (strftime("[%H:%M:%S]", localtime())
                             , error_string if error_string == '' else '字符串中有无法显示的字符。'))
        return _str

    @staticmethod
    def input(string):
        timestr = strftime("[%H:%M:%S]", localtime())
        return input(timestr+" "+string)

    @staticmethod
    def load_xls_sheet_list(xls_path):
        if not os.path.exists(xls_path):
            Danteng.log('[ %s ] 文件不存在！' % xls_path)
            return False

        try:
            data_wb = xlrd.open_workbook(xls_path)
        except xlrd.biffh.XLRDError as e:
            print(e)
            return False

        return data_wb.sheet_names()

    @staticmethod
    def load_xls(xls_path, sheet_name='', mode=''):
        try:
            return Danteng._load_xls(xls_path, sheet_name, mode)
        except Exception as e:
            Danteng.log('读取EXCEL文件发生错误，请检查工作薄中的格式是否符合规范。（%s）' % e)
            return False

    @staticmethod
    def _load_xls(xls_path, sheet_name='', mode=''):
        if not os.path.exists(xls_path):
            Danteng.log('[ %s ] 文件不存在！' % xls_path)
            return False

        try:
            data_wb = xlrd.open_workbook(xls_path)
        except xlrd.biffh.XLRDError as e:
            print(e)
            return False

        try:
            if sheet_name == '':
                data_ws = data_wb.sheet_by_index(0)
                sheet_name = data_ws['name']
            else:
                data_ws = data_wb.sheet_by_name(sheet_name)
        except xlrd.biffh.XLRDError as e:
            print(e)
            return False

        if data_ws.nrows < 1:
            Danteng.log('[ %s ] SHEET行数过少！' % sheet_name)
            return False
        if data_ws.ncols < 1:
            Danteng.log('[ %s ] SHEET列数过少！' % sheet_name)
            return False

        try:
            return Danteng._load_xls_worksheet(data_ws, mode)
        except Exception as e:
            Danteng.log('读取EXCEL文件发生错误，请检查工作薄中的格式是否符合规范。（%s）' % e)
            return False

    @staticmethod
    def _load_xls_worksheet(data_ws, mode):
        sheet_header = []
        sheet_data = {}
        index_list = []
        # 获取header
        if mode == 'noheader':
            # 无header，用列号作为header
            for i in range(0, data_ws.ncols):
                sheet_header.append(i)
        else:
            # 正常的有header情况
            for i in range(0, data_ws.ncols):
                header = data_ws.cell_value(0, i)
                header_type = data_ws.cell_type(0, i)

                if header_type == xlrd.XL_CELL_NUMBER:
                    if header % 1 == 0.0:
                        header = int(header)
                sheet_header.append(header)

        # 获取数据
        if mode == 'noheader':
            start_row = 0
        else:
            start_row = 1
        for i in range(start_row, data_ws.nrows):
            # 按第一列生成索引
            index = data_ws.cell_value(i, 0)
            index_type = data_ws.cell_type(i, 0)
            if index == '':
                continue
            if str(index)[0] == '!':
                continue

            index = Danteng._xls_value_check(index, index_type, index)
            index_list.append(index)

            # 按其他列生成dict数据
            sheet_data[index] = OrderedDict()
            for j in range(1, len(sheet_header)):
                header = str(sheet_header[j])
                if len(header) == 0:
                    continue
                if header[0] == '!':
                    continue
                if header[0] == '#':
                    header_output = header[1:]
                else:
                    header_output = header
                sheet_data[index][header_output] = Danteng._xls_value_check(data_ws.cell_value(i, j), data_ws.cell_type(i, j), header)

        return [sheet_data, index_list, sheet_header]

    @staticmethod
    def _xls_value_check(cell_value, cell_type, header=''):
        if cell_type == xlrd.XL_CELL_NUMBER:
            if cell_value % 1 == 0.0:
                cell_value = int(cell_value)
        elif cell_type == xlrd.XL_CELL_DATE:
            date_tuple = xlrd.xldate_as_tuple(cell_value, 0)
            if header != '':
                if header[0] == '#':
                    cell_value = '%d月%d日' % (date_tuple[1], date_tuple[2])
                else:
                    cell_value = '%4d-%02d-%02d' % (date_tuple[0], date_tuple[1], date_tuple[2])

        return cell_value

    @staticmethod
    def load_csv(csv_path, mode='', noheader=False, encoding='utf-8', delimiter=',', skip=''):
        csv_data = {'key_list': []}

        if not os.path.exists(csv_path):
            Danteng.log('%s 文件不存在。' % csv_path)
            return False

        with open(csv_path, 'r', newline='', encoding=encoding) as csv_file:
            reader = csv.reader(csv_file, delimiter=delimiter)
            header_list = []
            for row in reader:
                if reader.line_num == 1:
                    if noheader:
                        for i in range(0, len(row)):
                            header_list.append(i)
                    else:
                        header_list = row
                        if mode == 'ff14':
                            for i in range(0, len(header_list)):
                                find = re.findall(r'\d*\s(.*?)$', header_list[i])
                                if find:
                                    header_list[i] = find[0]
                        continue

                key = row[0]

                if skip != '' and key[0] == skip:
                    continue

                find = re.findall(b'^\xef\xbb\xbf(\d*?)$', key.encode())
                if find:
                    key = find[0].decode()
                row_data = {}
                for i in range(1, len(header_list)):
                    header = header_list[i]
                    row_data[header] = row[i]
                csv_data[key] = row_data
                csv_data['key_list'].append(key)

        return csv_data

    @staticmethod
    def file_download(url, path='', code='ansi', savename=''):
        if url == '':
            Danteng.log('下载的url不能为空。')
            return ''

        filename_list = url.split('/')
        if len(filename_list) > 0:
            filename = filename_list[len(filename_list)-1]
        else:
            Danteng.log('未找到文件名')
            return ''

        filetype_list = filename.split('.')
        if len(filetype_list) > 0:
            filetype = filetype_list[len(filetype_list)-1]
        else:
            filetype = ''

        if filetype in ['png', 'gif', 'jpg', 'jpeg']:
            code = 'binary'

        if path == '':
            path = os.getcwd()

        for i in range(3):
            try:
                response = requests.get(url, timeout=10)
                break
            except Exception as e: # 超时重新下载
                if i == 2:
                    Danteng.log('<%s>下载时，连接超时%d次，下载失败！' % (filename, i+1))
                    return ''
                else:
                    Danteng.log('<%s>下载时，连接超时，正在重试（超时%d次）...' % (filename, i+1))

        if response.status_code != 200:
            Danteng.log('文件<%s>获取失败！错误号：%d' % (filename, response.status_code))
            return ''

        if not os.path.exists(path):
            os.makedirs(path)

        if savename == '':
            savename = filename
        filepath = '%s\\%s' % (path, savename)
        if code == 'utf-8':
            file = codecs.open(filepath, 'w', 'utf-8')
            file.write(response.text)
        elif code == 'binary':
            file = open(filepath, 'wb')
            file.write(response.content)
        else:
            file = open(filepath, 'w')
            file.write(response.text)

        file.close()

        # Danteng.log('文件<%s>下载成功！' % filename)
        return filepath

    @staticmethod
    def load_config(config_file_path):
        config = {}
        if not os.path.exists(config_file_path):
            Danteng.log('配置文件[ %s ]不存在，请检查。' % config_file_path)
            return False

        config_cf = configparser.ConfigParser()
        config_cf.read(config_file_path)
        sections = config_cf.sections()

        for section in sections:
            config[section] = {}
            items = config_cf.items(section)
            for item in items:
                config[section][item[0]] = item[1]

        return config

    @staticmethod
    def save_obj(obj, path):
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
        return True

    @staticmethod
    def load_obj(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def save_to_csv(datas, headers, filename):
        with open(filename, 'wb') as f:
            writer = unicodecsv.writer(f)
            writer.writerow(headers)
            for key in datas:
                data = datas[key]
                line = []
                for header in headers:
                    line.append(data[header] if header in data else '')
                writer.writerow(line)

        with open(filename, 'r', encoding='UTF-8') as f:
            temp_file_content = f.read()
        with open(filename, 'w', encoding='utf_8_sig') as f:
            f.write(temp_file_content)
