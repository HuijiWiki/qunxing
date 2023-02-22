import json
import re
import os

from FoolDonkeyAssignment import pdx_logic, \
    pdx_replace_dict
from danteng import Danteng
from paradox_parser import ParadoxParser

# 处理本地化文件
# 对蠢驴思维做处理，防止找不到对应的文字


# 读取所有中英文本地化文本
def load_i18n(base_path, purge):
    obj_path = 'i18n.obj'
    if (not purge) and os.path.exists(obj_path):
        temp = Danteng.load_obj(obj_path)
        return dict(temp[0]), dict(temp[1])

    zhcn_path = 'localisation\\simp_chinese'
    zhcn_path_mod = r'L:\python_working_dir\stellaris\localisation'
    en_path = 'localisation\\english'
    # 读取本地化文档
    i18n_zhcn_map = dict()
    i18n_en_map = dict()

    Danteng.log('----------英文文本----------')
    for filename in os.listdir(os.path.join(base_path, en_path)):
        if filename[-4:] == '.yml':
            i18n_en_map.update(_load_i18n(os.path.join(base_path, en_path, filename)))

    i18n_zhcn_map.update(i18n_en_map)

    Danteng.log('----------中文文本----------')
    for filename in os.listdir(os.path.join(base_path, zhcn_path)):
        if filename[-4:] == '.yml':
            i18n_zhcn_map.update(_load_i18n(os.path.join(base_path, zhcn_path, filename)))

    Danteng.log('----------修正文本----------')
    for filename in os.listdir(zhcn_path_mod):
        if filename[-4:] == '.yml':
            i18n_zhcn_map.update(_load_i18n(os.path.join(zhcn_path_mod, filename)))

    Danteng.save_obj((i18n_zhcn_map, i18n_en_map), obj_path)
    return i18n_zhcn_map, i18n_en_map


def load_synced(base_path, purge):
    obj_path = 'i18n.obj'
    if (not purge) and os.path.exists(obj_path):
        temp = Danteng.load_obj(obj_path)
        return dict(temp[0]), dict(temp[1])

    zhcn_path = base_path
    en_path = base_path

    # 读取本地化文档
    i18n_zhcn_map = dict()
    i18n_en_map = dict()

    for filename in os.listdir(os.path.join(base_path, en_path)):
        if filename[-4:] == '.yml' and filename[-7:] != '_SC.yml':
            i18n_en_map.update(_load_i18n(os.path.join(base_path, en_path, filename)))

    i18n_zhcn_map.update(i18n_en_map)

    for filename in os.listdir(zhcn_path):
        if filename[-7:] == '_SC.yml':
            i18n_zhcn_map.update(_load_i18n(os.path.join(zhcn_path, filename)))

    Danteng.save_obj((i18n_zhcn_map, i18n_en_map), obj_path)
    return i18n_zhcn_map, i18n_en_map


def _load_i18n(path):
    i18n = ParadoxParser(path)
    return i18n.get_data()[0]


# 替换掉以下几个蠢驴规则:
#   * MOD_开头的
#   * \$(.*?)\$ 文字变量
def replace(in_map):
    out_map = dict()
    for key in in_map:
        # 替换掉 '$(.*?)$'
        findall = re.findall(r'\$(.*?)\$', in_map[key])
        for find_key in findall:
            if find_key == 'RESOURCE':
                break
            if find_key in pdx_replace_dict:
                in_map[key] = in_map[key].replace('$%s$' % find_key, '$%s$' % pdx_replace_dict[find_key])
                find_key = pdx_replace_dict[find_key]
            if find_key in in_map:
                new_text = in_map[find_key]
                in_map[key] = in_map[key].replace('$%s$' % find_key, new_text)
            elif find_key + '_01' in in_map:
                new_text = in_map[find_key + '_01']
                in_map[key] = in_map[key].replace('$%s$' % find_key, new_text)
                all_text = in_map[key]
                for i in range(2, 99):
                    temp_key = '_%02d' % i
                    new_key = key + temp_key
                    if find_key + temp_key in in_map:
                        all_text +=' 或 '
                        new_text = in_map[find_key + temp_key]
                        temp_text = in_map[key].replace('$%s$' % find_key, new_text)
                        out_map[new_key] = temp_text
                        all_text +='\"' + temp_text + '\"'
                        # Danteng.log(key + '|' + new_key + '|' + out_map[new_key])
                    else:
                        break
                in_map[key] = all_text
                # Danteng.log('多种情况：' + key + '|' + in_map[key])
            elif find_key + '_1' in in_map:
                new_text = in_map[find_key + '_1']
                in_map[key] = in_map[key].replace('$%s$' % find_key, new_text)
            elif len(find_key)>=5 and find_key[0:-5] + '_1_desc' in in_map:
                new_text = in_map[find_key[0:-5] + '_1_desc']
                in_map[key] = in_map[key].replace('$%s$' % find_key, new_text)
            # elif find_key in fool_donkey_dict:
            #     in_map[key] = in_map[key].replace('$%s$' % find_key, fool_donkey_dict[find_key])
            # else:
            #     Danteng.log('原文没找到' + find_key + '\t\t\t\t' + key + ': ' + in_map[key])
            z = 1
        # in_map[key] = in_map[key].replace('\\n', '<br />')
        # # 替换掉 'MOD'开头的
        if key[0:4] == 'MOD_' or key[0:4] == 'mod':
            out_map[key[4:].lower()] = in_map[key]
            # Danteng.log(key + '|' + key[4:].lower() + '|' + zhcn_map[key[4:].lower()])
        # else:
        #     out_map[key] = in_map[key]
        # Danteng.log(in_map[key])
    for key in pdx_replace_dict:
        if pdx_replace_dict[key] in in_map:
            out_map[key] = in_map[pdx_replace_dict[key]]
        else:
            out_map[key] = pdx_replace_dict[key]
            Danteng.log('没找到' + pdx_replace_dict[key])
    for key in in_map:
        if key != key.lower() and (not key.lower() in in_map) and (not key.lower() in out_map):
            out_map[key.lower()] = in_map[key]
    in_map.update(out_map)
    return in_map


def processor(path, synced_path='', purge=True):
    # 读取本地化文档
    i18n_zhcn_map, i18n_en_map = load_i18n(path, purge)

    for i in range(2):
        i18n_en_map = replace(i18n_en_map)
        i18n_zhcn_map = replace(i18n_zhcn_map)

    for item in pdx_logic:
        if pdx_logic[item]['value'] in i18n_zhcn_map:
            pdx_logic[item]['value'] = i18n_zhcn_map[pdx_logic[item]['value']]
    if synced_path != '':
        zhcn_map, en_map = load_synced(synced_path, purge)
        zhcn_map.update(i18n_zhcn_map)
        en_map.update(i18n_en_map)
        i18n_zhcn_map = zhcn_map
        i18n_en_map = en_map
    return i18n_zhcn_map, i18n_en_map


if __name__ == '__main__':
    data_path = 'F:\\Steam\\steamapps\\common\\Stellaris\\'

    # 输出json方便查看
    cn_map, en_map = processor(data_path, True)
    cn_json = json.dumps(cn_map, ensure_ascii=False)
    with open('F:\\PycharmProjects\\stellaris_data_processer\\json\\cn.json', 'w', encoding='UTF-8') as f:
        f.write(cn_json)

    en_json = json.dumps(en_map, ensure_ascii=False)
    with open('F:\\PycharmProjects\\stellaris_data_processer\\json\\en.json', 'w', encoding='UTF-8') as f:
        f.write(en_json)
    z = 1
