import colorsys
import re

from danteng import Danteng


def tech_unlocks(item, tech_prerequisites, tags, component_sets):
    if 'prerequisites' in item:
        if 'component_set' in item:
            if item['component_set'] in component_sets:
                Danteng.log(item['component_set'] + '已有套件了')
                return tech_prerequisites
            else:
                Danteng.log(item['component_set'] + '已加入套件')
                component_sets.append(item['component_set'])
        for i in range(len(item['prerequisites'])):
            temp_str = ''
            key = item['prerequisites'][i].replace('"', '')
            if key in tech_prerequisites:
                temp_str = tech_prerequisites[key]
            tech_prerequisites[key] = temp_str + '\\n' + '§H' + tags + '：§!' + item['zhcn_name']
    return tech_prerequisites


def zhcn(item, i18n_zhcn_map, i18n_en_map, empty=False):
    if type(item) != str:
        Danteng.log('错误：文本传入参数不是字符串')
        return '', ''
    if item in i18n_zhcn_map:
        zhcn_name = i18n_zhcn_map[item]
    elif item in i18n_en_map:  # 汉化未完成时临时占位
        zhcn_name = i18n_en_map[item]
    elif empty:
        zhcn_name = ''
    else:
        zhcn_name = item
    if item in i18n_en_map:
        en_name = i18n_en_map[item]
    elif empty:
        en_name = ''
    else:
        en_name = item
    return zhcn_name, en_name


def hsv2rgb(hsv_str):
    a = None
    hsv_color = re.findall(r'hsv\s*{\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*?)\s*}', hsv_str.group(0))
    h = float(hsv_color[0][0])
    s = float(hsv_color[0][1])
    v = float(hsv_color[0][2])
    if hsv_color[0][3] != '':
        a = int(float(hsv_color[0][3]) * 255)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return dig2hex(r, g, b, a)


def rgb_hex(rgb_str):
    a = None
    rgb_color = re.findall(r'rgb\s*{\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*?)\s*}', rgb_str.group(0))
    r = int(rgb_color[0][0])
    g = int(rgb_color[0][1])
    b = int(rgb_color[0][2])
    if rgb_color[0][3] != '':
        a = int(rgb_color[0][3])
    return dig2hex(r, g, b, a)


def dig2hex(r, g, b, a):
    if r > 255:
        r = 255
    if g > 255:
        g = 255
    if b > 255:
        b = 255
    if a:
        color_str = hex(r * 0x1000000 + g * 0x10000 + b * 0x100 + a)
        color_str = color_str[2:]
        if len(color_str) < 8:
            for i in range(0, 8 - len(color_str)):
                color_str = '0' + color_str
    else:
        color_str = hex(r * 0x10000 + g * 0x100 + b)
        color_str = color_str[2:]
        if len(color_str) < 6:
            for i in range(0, 6 - len(color_str)):
                color_str = '0' + color_str
    return color_str


def var_processor(data, val_dict):
    if len(val_dict) == 0:
        return data
    if type(data) == list:
        for i in range(len(data)):
            if type(data[i]) == str:
                if data[i][0] == '@':
                    data = val_dict[data]
            else:
                var_processor(data[i], val_dict)
    else:
        for key in data:
            if type(data[key]) == str and len(data[key]) > 0:
                if data[key][0] == '@':
                    if data[key] not in val_dict:
                        z = 1
                    data[key] = val_dict[data[key]]
            elif type(data[key]) == list:
                for i in range(len(data[key])):
                    if type(data[key][i]) == str:
                        if data[key][i][0] == '@':
                            data[key] = val_dict[data[key]]
                    else:
                        var_processor(data[key][i], val_dict)
            else:
                var_processor(data[key], val_dict)
    return data
