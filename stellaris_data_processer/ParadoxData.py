import json
import os
import re
from abc import abstractmethod
from collections import OrderedDict

from FoolDonkeyAssignment import pdx_logic, pdx_resource, pdx_replace_dict, \
    preprocess_pdx_dict, pdx_modifier, pdx_logic_word
from SaveToExcel import save_to_excel
from danteng import Danteng
from paradox_parser import ParadoxParser
from processor import processor
from utilities import var_processor


class ParadoxData:
    base_path = 'F:\\Games\\Steam\\steamapps\\common\\Stellaris\\'
    synced_path = 'F:\\Games\\Steam\\steamapps\\common\\Stellaris\\localisation_synced\\'
    i18n_zhcn_map, i18n_en_map = processor(base_path, synced_path)
    version = '2.3.0'
    icon_dict = OrderedDict()
    scripted_variables = OrderedDict()
    all_data = OrderedDict()
    indentation = r'<div style="margin-left:14px">'
    tech_prerequisites = OrderedDict()
    tech_prerequisites_cat = []
    base_key_list = ['key', 'main_category', 'version', 'zhcn_name', 'en_name', 'zhcn_desc', 'en_desc', '_index']
    loc_icon = []

    # 修正
    modifiers = ['modifier', 'planet_modifier', 'country_modifier', 'system_modifier', 'station_modifier',
                 'ship_modifier', 'orbit_modifier', 'army_modifier', 'pop_modifier', 'self_modifier', 'adjacency_bonus']
    logics = ['random_weight', 'weight_modifier', 'potential', 'orbital_weight', 'drop_weight', 'ai_weight',
              'spawn_chance', 'allow', 'ai_allow', 'show_tech_unlock_if', 'destroy_if', 'active', 'weight', 'playable',
              'election_candidates', 'condition', 'ai_wants', 'potential_country', 'triggered_station_modifier',
              'assembling_modifier']

    # 还有triggered_planet_modifier和planet_modifier_with_pop_trigger，蠢驴暂时未启用

    def __init__(self, item_category):
        self.item_category = item_category
        self.data = OrderedDict()
        self.raw_data = OrderedDict()
        self.local_variables = OrderedDict()
        self.local_variables.update(self.scripted_variables)
        self.all_keys = []

    # 版本，通用
    def set_version(self, version):
        self.version = version

    # 图标，一次设置，一直使用
    def set_icons(self, icons):
        self.icon_dict.update(icons)

    # 蠢驴预置变量，一次设置，一直使用
    def set_scripted_variables(self, scripted_variables):
        self.scripted_variables.update(scripted_variables)

    # 文本处理，主要是图标和成就
    def text_processor(self, filename):
        common_path = self.base_path + 'common\\'
        common_data = dict()
        pp = ParadoxParser(os.path.join(common_path, filename), self.item_category)
        data = pp.get_data()[0]
        common_data.update(data)
        return common_data

    # 处理common的指定子文件夹的内容
    def common_processor(self, category_path, is_common=True):
        if is_common:
            common_path = self.base_path + 'common\\'
        else:
            common_path = self.base_path
        common_data = dict()
        for filename in os.listdir(os.path.join(common_path, category_path)):
            if filename[-4:] == '.txt':
                pp = ParadoxParser(os.path.join(common_path, category_path, filename), self.item_category)
                [data, global_var] = pp.get_data()
                self.local_variables.update(global_var)
                # self.scripted_variables.update(global_var)
                common_data.update(data)
        if len(self.scripted_variables) != 0:
            # var_processor(common_data, self.scripted_variables)
            var_processor(common_data, self.local_variables)
        self.raw_data = common_data
        self.add_important_keys()
        return self.raw_data

    # 添加一些重要字段，方便查询
    def add_important_keys(self):
        temp_raw = OrderedDict()
        change_key = False
        for key, info in self.raw_data.items():
            temp = OrderedDict()
            if self.item_category == 'pop_jobs':
                temp['key'] = 'job_' + key
                change_key = True
            elif self.item_category == 'pop_categories':
                temp['key'] = 'pop_cat_' + key
                change_key = True
            else:
                temp['key'] = key
            temp['main_category'] = self.item_category
            temp['version'] = self.version

            # zhcn_name, en_name 名称
            temp['zhcn_name'], temp['en_name'] = self.zhcn(temp['key'])
            # zhcn_desc, en_desc 描述
            temp['zhcn_desc'], temp['en_desc'] = self.zhcn(temp['key'] + '_desc', True)

            instruction = ''
            if 'tags' in info:
                for i in info['tags']:
                    instruction += self.zhcn(i)[0] + '\\n'
                temp['instruction'] = instruction[0:-2]
                Danteng.log(temp['zhcn_name'] + '\\n' + temp['instruction'])

            # 保留原名称对应的原始数据，同时展示出具体效果
            # 以防翻译内容更新，重新从翻译中读取
            for modifier_name in self.modifiers:
                if modifier_name in info:
                    if len(info[modifier_name]) == 0:
                        info.pop(modifier_name)
                    else:
                        Danteng.log('\n' + temp['zhcn_name'] + '的modifier：' + modifier_name)
                        name = 'zhcn_' + modifier_name
                        temp[name] = self.modifier_processor(info[modifier_name])

            for logic_name in self.logics:
                if logic_name in info:
                    if len(info[logic_name]) == 0:
                        info.pop(logic_name)
                    else:
                        Danteng.log('\n' + temp['zhcn_name'] + '的logic：' + logic_name)
                        if logic_name in pdx_logic:
                            logic_zhcn_name = pdx_logic[logic_name]['value']
                        else:
                            logic_zhcn_name = self.zhcn(logic_name)[0]
                        self.logic_it(logic_name, info, logic_zhcn_name)
            temp.update(info)

            # possible
            if 'possible' in info:
                Danteng.log('\n' + temp['zhcn_name'] + '的possible：')
                name = 'possible_desc'
                temp[name] = self.possible_processor(info['possible'])
                temp[name] = self.modifier_replace(temp[name])
                Danteng.log(temp[name])

            if temp['main_category'] == 'pop_faction_types':
                temp['icon'] = self.icon_dict['GFX_faction_icon_' + temp['key']]['icon']
            if 'icon' in info:
                temp['icon'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', info['icon'].replace('"', ''))
                if temp['icon'] in self.icon_dict:
                    temp['icon'] = self.icon_dict[temp['icon']]['icon']
            # 价格和维护费
            if 'resources' in info:
                if 'cost' in info['resources']:
                    temp['cost_detail'] = ''
                    if isinstance(info['resources']['cost'], list):
                        for case_id in range(len(info['resources']['cost'])):
                            sub_case = info['resources']['cost'][case_id]
                            if 'trigger' in sub_case:
                                temp['cost_detail'] += '如果' + self.logic_processor(sub_case['trigger'])[0] + '\n则花费'
                            else:
                                temp['cost_detail'] += '默认则花费'
                            for sub_name in sub_case:
                                if sub_name != 'trigger':
                                    temp['cost_detail'] += '£' + sub_name + sub_case[sub_name]
                            temp['cost_detail'] += '\n'
                    else:
                        for res, cost_value in info['resources']['cost'].items():
                            temp['cost_detail'] += '£' + res + cost_value
                try:
                    if 'upkeep' in info['resources']:
                        temp['upkeep_detail'] = ''
                        for res, cost_value in info['resources']['upkeep'].items():
                            temp['upkeep_detail'] += '£' + res + cost_value
                    if 'produces' in info['resources']:
                        temp['produces_detail'] = ''
                        for res, cost_value in info['resources']['produces'].items():
                            temp['produces_detail'] += '£' + res + cost_value
                except:
                    self.logic_it('resources', temp)
                if 'min_upgrade_cost' in temp:
                    temp['zhcn_min_upgrade_cost'] = ''
                    for res, cost_value in info['min_upgrade_cost'].items():
                        temp['zhcn_min_upgrade_cost'] += '£' + res + cost_value
            # 前置科技
            if 'prerequisites' in temp:
                if len(temp['prerequisites']) == 0:
                    temp.pop('prerequisites')
                else:
                    find = re.findall(r'\"(.*?)\"', temp['prerequisites'][0])
                    if find:
                        temp['prerequisites'] = find
            if 'show_in_tech' in temp:
                temp['show_in_tech'] = temp['show_in_tech'].replace('"', '')
            # 最后更新数据
            self.raw_data[key] = temp
        if change_key:
            for key, info in self.raw_data.items():
                temp_raw[info['key']] = info
            self.raw_data = temp_raw
            z = 2

    def zhcn(self, item, empty=False):
        if type(item) != str:
            Danteng.log('错误：文本传入参数不是字符串')
            return '', ''
        if item in self.i18n_zhcn_map:
            zhcn_name = self.i18n_zhcn_map[item]
        elif item + 'effect' in self.i18n_zhcn_map:  # triggers effects
            zhcn_name = self.i18n_zhcn_map[item + 'effect']
        elif item in self.i18n_en_map:  # 汉化未完成时临时占位
            zhcn_name = self.i18n_en_map[item]
        elif empty:
            zhcn_name = ''
        else:
            zhcn_name = item
        if item in self.i18n_en_map:
            en_name = self.i18n_en_map[item]
        elif empty:
            en_name = ''
        else:
            en_name = item
        return zhcn_name, en_name

    def modifier_processor(self, modifier_dict):
        name_str = ''
        if 'description' in modifier_dict:
            name_str = self.i18n_zhcn_map[modifier_dict['description']]
            if 'description_parameters' in modifier_dict:
                for item in modifier_dict['description_parameters']:
                    value = modifier_dict['description_parameters'][item]
                    num = float(value)
                    is_int = False
                    if type(num) == float and num % 1 == 0.0:
                        num = int(num)
                        is_int = True
                    if is_int:
                        para_str = '%+g' % num
                    else:
                        para_str = '%+g%%' % (num * 100)
                    name_str = re.sub(r'\$' + item + '.*?\$', ('§G' + para_str + '§!'), name_str)
            return name_str
        if type(modifier_dict) == str:
            key = modifier_dict.replace('"', '')
            if key in self.i18n_zhcn_map:
                name_str = self.i18n_zhcn_map[key]
            elif key.upper in self.i18n_zhcn_map:
                name_str = self.i18n_zhcn_map[key.upper()]
            elif 'country_' + key in self.i18n_zhcn_map:
                name_str = self.i18n_zhcn_map['country_' + key]
            elif key in pdx_replace_dict:
                if pdx_replace_dict[key] in self.i18n_zhcn_map:
                    name_str = self.i18n_zhcn_map[pdx_replace_dict[key]]
                else:
                    name_str = self.i18n_en_map[pdx_replace_dict[key]]
            elif key in self.i18n_en_map:
                name_str = self.i18n_en_map[key]
            elif key.upper in self.i18n_en_map:
                name_str = self.i18n_en_map[key.upper()]
            elif 'country_' + key in self.i18n_en_map:
                name_str = self.i18n_en_map['country_' + key]
            else:
                name_str = key
            name_str.strip()
            Danteng.log(name_str)
            return name_str
        for key, value in modifier_dict.items():
            # mod_key = 'MOD_' + key
            if key in self.i18n_zhcn_map:
                name_str += self.i18n_zhcn_map[key] + '：'
            elif key.upper in self.i18n_zhcn_map:
                name_str += self.i18n_zhcn_map[key.upper()] + '：'
            elif 'country_' + key in self.i18n_zhcn_map:
                name_str += self.i18n_zhcn_map['country_' + key] + '：'
            elif 'mod_' + key in self.i18n_zhcn_map:
                name_str += self.i18n_zhcn_map['mod_' + key] + '：'
            elif key[-5:] == '_mult' and key[0:-5] in self.i18n_zhcn_map:
                name_str += self.i18n_zhcn_map[key[0:-5]] + '：'
            elif key in pdx_replace_dict:
                name_str += self.i18n_zhcn_map[pdx_replace_dict[key]] + '：'
            elif key in self.i18n_en_map:
                name_str += self.i18n_en_map[key] + '：'
            elif key.upper in self.i18n_en_map:
                name_str += self.i18n_en_map[key.upper()] + '：'
            elif 'country_' + key in self.i18n_en_map:
                name_str += self.i18n_en_map['country_' + key] + '：'
            elif key[-5:] == '_mult' and key[0:-5] in self.i18n_en_map:
                name_str += self.i18n_en_map[key[0:-5]] + '：'
            elif key in pdx_replace_dict:
                name_str += self.i18n_en_map[pdx_replace_dict[key]] + '：'
            else:
                name_str = key

            temp_str = ''
            if key == 'custom_tooltip':
                name_str = self.zhcn(value)[0]
            elif type(value) == str and value != '':
                if value == 'yes':
                    temp_str = '▲'
                elif value == 'no':
                    temp_str = '△'
                else:
                    try:
                        num = float(value)
                    except:
                        num = 0
                        z = 1
                    if type(value) == float and value % 1 == 0.0:
                        num = int(value)
                    preprocess_pdx_dict(key)
                    if pdx_modifier[key]['mode'] == 'add':
                        temp_str = '%+g' % num
                    elif pdx_modifier[key]['mode'] == 'add_perc':
                        temp_str = '%+g%%' % num
                    else:
                        temp_str = '%+g%%' % (num * 100)
                    if (pdx_modifier[key]['positive'] == 'true' and num > 0) \
                            or (pdx_modifier[key]['positive'] == 'false' and num < 0):
                        temp_str = '§G' + temp_str + '§!'
                    else:
                        temp_str = '§R' + temp_str + '§!'
            name_str += temp_str + '\\n'
            # if isinstance(target,int) :
        find = re.findall(r'\$.*?\$', name_str)
        if find:
            for item in find:
                find_key = item[1:-1]
                if find_key in self.i18n_zhcn_map:
                    name_str = name_str.replace(item, self.i18n_zhcn_map[find_key])
                elif find_key in self.i18n_en_map:
                    name_str = name_str.replace(item, self.i18n_en_map[find_key])
        name_str.strip()
        Danteng.log(name_str[0:-2])
        return name_str[0:-2]

    def logic_processor(self, logic_item, name='', flag_not=False, positive=True,
                        is_list_item=False, has_text=False):
        logic_str = ''
        temp_str = ''
        has_var = False
        non_flag = False

        if flag_not and name != '':
            name = 'not_' + name

        positive = positive ^ flag_not  # flag_not和positive同真为假，同假为真，恰好符合异或
        if name == 'NOT':
            positive = not (positive ^ False)
        elif name in pdx_resource:
            logic_str = '£' + pdx_resource[name] + '§H' + self.i18n_zhcn_map[name] + '§!'
        elif name in pdx_logic:
            name_str = pdx_logic[name]['value']
            if 'positive' in pdx_logic[name]:
                positive = not (positive ^ pdx_logic[name]['positive'])
            else:
                non_flag = True

            if re.findall(r'\$.*?\$', name_str):
                has_var = True

            if non_flag:
                temp_str = '№'
            else:
                if positive:
                    temp_str = '▲'
                else:
                    temp_str = '△'

            logic_str += temp_str + name_str
        elif name == '':
            if non_flag:
                temp_str += '№'
            else:
                if positive:
                    temp_str += '▲'
                else:
                    temp_str += '△'
        else:
            logic_str += name

        if isinstance(logic_item, str):
            logic_item = logic_item.replace('"', '')
            if logic_item in pdx_resource:
                logic_item = '£' + pdx_resource[logic_item] + '§H' + self.i18n_zhcn_map[logic_item] + '§!'
            elif logic_item in pdx_logic:
                logic_item = '§H' + pdx_logic[logic_item]['value'] + '§!'
            elif logic_item in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map[logic_item] + '§!'
            elif ('pft_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['pft_' + logic_item] + '§!'
            elif ('personality_type_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['personality_type_' + logic_item] + '§!'
            elif ('personality_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['personality_' + logic_item] + '§!'
            elif ('casus_belli_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['casus_belli_' + logic_item] + '§!'
            elif ('SUBJECT_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['SUBJECT_' + logic_item] + '§!'
            elif ('sm_' + logic_item) in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map['sm_' + logic_item] + '§!'
            elif (logic_item + '_effect') in self.i18n_zhcn_map:
                logic_item = '§H' + self.i18n_zhcn_map[logic_item + '_effect'] + '§!'
            elif logic_item in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map[logic_item] + '§!'
            elif ('pft_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['pft_' + logic_item] + '§!'
            elif ('personality_type_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['personality_type_' + logic_item] + '§!'
            elif ('personality_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['personality_' + logic_item] + '§!'
            elif ('casus_belli_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['casus_belli_' + logic_item] + '§!'
            elif ('SUBJECT_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['SUBJECT_' + logic_item] + '§!'
            elif ('sm_' + logic_item) in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map['sm_' + logic_item] + '§!'
            elif (logic_item + '_effect') in self.i18n_en_map:
                logic_item = '§H' + self.i18n_en_map[logic_item + '_effect'] + '§!'
            elif len(self.raw_data) != 0 and logic_item in self.raw_data and 'zhcn_name' in self.raw_data[logic_item]:
                logic_item = '§H' + self.raw_data[logic_item]['zhcn_name'] + '§!'
            if has_var:
                logic_str = re.sub(r'\$.*?\$', logic_item, logic_str)
            else:
                if is_list_item:
                    logic_str += temp_str + logic_item
                else:
                    logic_str += logic_item
        elif isinstance(logic_item, dict):
            if 'text' in logic_item:
                has_text = True
                logic_item['text'] = logic_item['text'].replace('"', '')
                if logic_item['text'] in self.i18n_zhcn_map:
                    logic_str = temp_str + self.i18n_zhcn_map[logic_item['text']].replace('§R', '§W')
                elif logic_item['text'] in self.i18n_en_map:
                    logic_str = temp_str + self.i18n_en_map[logic_item['text']].replace('§R', '§W')
                else:
                    Danteng.log("————" + logic_item['text'] + '没找到')
                    logic_str = temp_str + logic_item['text']
            elif 'fail_text' in logic_item:
                has_text = True
                logic_item['fail_text'] = logic_item['fail_text'].replace('"', '')
                if logic_item['fail_text'] in self.i18n_zhcn_map:
                    if '£trigger_no' in logic_item['fail_text']:
                        logic_str = temp_str + self.i18n_zhcn_map[logic_item['fail_text']]
                    else:
                        logic_str = temp_str + '△' + self.i18n_zhcn_map[logic_item['fail_text']]
                elif logic_item['fail_text'] in self.i18n_en_map:
                    logic_str = temp_str + '△' + self.i18n_en_map[logic_item['fail_text']]
                else:
                    Danteng.log("————" + logic_item['fail_text'] + '没找到')
                    logic_str = temp_str + logic_item['fail_text']
            elif 'custom_tooltip' in logic_item and isinstance(logic_item['custom_tooltip'], str):
                has_text = True
                logic_item['custom_tooltip'] = logic_item['custom_tooltip'].replace('"', '')
                if logic_item['custom_tooltip'] in self.i18n_zhcn_map:
                    logic_str = temp_str + self.i18n_zhcn_map[logic_item['custom_tooltip']].replace('§R', '§W')
                elif logic_item['custom_tooltip'] in self.i18n_en_map:
                    logic_str = temp_str + self.i18n_en_map[logic_item['custom_tooltip']].replace('§R', '§W')
                else:
                    Danteng.log("————" + logic_item['custom_tooltip'] + '没找到')
                    logic_str = temp_str + logic_item['custom_tooltip']
            elif name == 'NOT':
                for item in logic_item:
                    logic_str += self.logic_level(self.logic_processor(logic_item[item], item, True, positive=positive)
                                                  [0])
            else:
                for item in logic_item:
                    logic_str += self.logic_level(self.logic_processor(logic_item[item], item, positive=positive)
                                                  [0])
        elif isinstance(logic_item, list):
            if has_var:
                logic_str = re.sub(r'\$.*?\$', '', logic_str)
            for i in range(len(logic_item)):
                logic_str += self.logic_level(self.logic_processor(logic_item[i], positive=positive,
                                                                   is_list_item=True)[0])
        else:
            Danteng.log('这行没处理:\t\t' + str(logic_item))
        return logic_str, has_text

    def logic_level(self, logic_str):
        return self.indentation + logic_str + '</div>'

    def possible_processor(self, modifier_dict, flag=True, title='', inside=False):
        name_str = ''
        if type(modifier_dict) == list:
            name_str = ''
            for i in range(len(modifier_dict)):
                name_str += self.possible_processor(modifier_dict[i], flag, title, inside)
        elif type(modifier_dict) != str:
            if 'text' in modifier_dict:
                if flag:
                    temp_str = '▲'
                else:
                    temp_str = '△'
                i18n_str = self.zhcn(modifier_dict['text'].replace('"', ''))[0]
                name_str += temp_str + i18n_str + '\\n'
            elif 'fail_text' in modifier_dict:
                if flag:
                    temp_str = '▲'
                else:
                    temp_str = '△'
                i18n_str = self.zhcn(modifier_dict['fail_text'].replace('"', ''))[0]
                name_str += temp_str + i18n_str + '\\n'
            else:
                if title in pdx_logic_word:
                    if title != 'NOR':
                        temp_str = '▲'
                    else:
                        temp_str = '△'
                    name_str += temp_str + pdx_logic[title]['value'] + '\\n'
                    inside = True
                for key, value in modifier_dict.items():
                    if key == 'NOR':
                        flag = False
                    sub_str = self.possible_processor(value, flag, key, inside)
                    if inside:
                        name_str += self.logic_level(sub_str)
                    else:
                        name_str += sub_str
        else:
            modifier_dict = modifier_dict.replace('"', '')
            if flag:
                temp_str = '▲拥有'
            else:
                temp_str = '△不接受'
            if modifier_dict in pdx_logic:
                temp_str += '§Y' + pdx_logic[modifier_dict]['value'] + '§!' + '\\n'
            elif modifier_dict in self.i18n_zhcn_map:
                temp_str += '§Y' + self.i18n_zhcn_map[modifier_dict] + '§!' + '\\n'
            elif modifier_dict in self.i18n_en_map:
                temp_str += '§Y' + self.i18n_en_map[modifier_dict] + '§!' + '\\n'
            name_str += temp_str
        name_str.strip()
        Danteng.log(name_str)
        return name_str

    def logic_it(self, logic_name, value, name_str=''):
        if logic_name in value and len(value[logic_name]) > 0:
            logic_str = self.logic_processor(value[logic_name])
            logic_str = re.sub(r'\\n(\s*?)\\n', r'\\n\1〓--------------\\n', logic_str[0])
            logic_str = re.sub(r'系数 × ', r'如果满足下列条件，则系数 × ', logic_str)
            if logic_str[0] == '№':
                logic_str = logic_str[1:]
            logic_str = self.modifier_replace(logic_str)
            if name_str == '' and 'zhcn_name' in value:
                Danteng.log('\n' + value['zhcn_name'] + '的logic：' + logic_str)
            elif name_str == '' and 'key' in value:
                Danteng.log('\n' + value['key'] + '的logic：' + logic_str)
            elif name_str == '':
                Danteng.log('\n' + '临时未知项目的logic：' + logic_str)
            else:
                Danteng.log('\n' + name_str + '的logic：' + logic_str)
            value[logic_name + '_logic'] = logic_str

    def choice(self, item, depth=0):
        desc = ''
        temp_str = ''
        if 'if' in item:
            if 'limit' in item['if']:
                desc += '\\n如果满足条件§H'
                for name, value in item['if']['limit'].items():
                    if name in self.i18n_zhcn_map:
                        i18n_name = self.i18n_zhcn_map[name]
                    elif name in self.i18n_en_map:
                        i18n_name = self.i18n_en_map[name]
                    else:
                        i18n_name = name
                    desc += temp_str + i18n_name + value
                desc += '§!：'
            if 'custom_tooltip' in item['if']:
                name = item['if']['custom_tooltip']
                if name in self.i18n_zhcn_map:
                    i18n_name = self.i18n_zhcn_map[name]
                elif name in self.i18n_en_map:
                    i18n_name = self.i18n_en_map[name]
                else:
                    i18n_name = name
                desc += i18n_name
            if 'else' in item['if']:
                desc += '\\n§L不满足上述条件时：§E\\n' + self.choice(item['if']['else'], depth + 1)
                if 'custom_tooltip' in item['if']['else']:
                    name = item['if']['custom_tooltip']
                    if name in self.i18n_zhcn_map:
                        i18n_name = self.i18n_zhcn_map[name]
                    elif name in self.i18n_en_map:
                        i18n_name = self.i18n_en_map[name]
                    else:
                        i18n_name = name
                    desc += i18n_name
        if depth > 0:
            desc = self.logic_level(desc)
        return desc

    @staticmethod
    def modifier_replace(string):
        string = re.sub(r'№(权力制度)\\n.*?基础值\s*?=\s*?§(.*?)§!', r'▲拥有§\2§!\1', string)
        string = re.sub(r'№(权力制度)\\n.*?基础值\s*?≠\s*?§(.*?)§!', r'△没有§\2§!\1', string)
        string = re.sub(r'№(思潮)\\n.*?基础值\s*?=\s*?§(.*?)§!', r'▲拥有§\2§!\1', string)
        string = re.sub(r'№(思潮)\\n.*?基础值\s*?≠\s*?§(.*?)§!', r'△没有§\2§!\1', string)
        string = re.sub(r'№(国家类型)\\n.*?基础值\s*?=\s*?§(.*?)§!', r'▲\1是§\2§!', string)
        string = re.sub(r'№(国家类型)\\n.*?基础值\s*?≠\s*?§(.*?)§!', r'△\1不是§\2§!', string)
        string = re.sub(r'▲拥有§Y是§!\\n', r'▲始终可用', string)
        string = re.sub(r'always: §H否§!', r'△始终不可用', string)
        string = re.sub(r'always: §H是§!', r'▲始终可用', string)
        string = re.sub(r'always§H否§!', r'△始终不可用', string)
        string = re.sub(r'always§H是§!', r'▲始终可用', string)
        string = re.sub(r'is_slave_tile_or_planet: §H是§!', r'▲允许在奴隶地块或星球建设', string)
        string = re.sub(r'is_slave_tile_or_planet: §H否§!', r'△不允许在奴隶地块或星球建设', string)
        string = re.sub(r'is_robot_tile_or_planet: §H是§!', r'▲允许在机器人地块或星球建设', string)
        string = re.sub(r'is_robot_tile_or_planet: §H否§!', r'△不允许在机器人地块或星球建设', string)
        string = re.sub(r'any_owned_planet: \\n※\d*not_is_same_value: §H来自§!\\n※\d*△拥有', r'△任意星球都没有', string)
        string = re.sub(r'not_unrest: >', r'不满≤', string)
        string = re.sub(r'has_living_standard: \\n※\d*country: §H星球拥有者§!\\n※\d*№', r'▲有生活标准：', string)
        string = re.sub(r'№£trigger', r'£trigger', string)
        string = re.sub(r'not_years_passed: >', r'年数 <', string)
        string = re.sub(r'not_has_seen_any_bypass: wormhole', r'△尚未发现任何虫洞', string)
        string = re.sub(r'not_has_seen_any_bypass: gateway', r'△尚未发现任何星门', string)
        string = re.sub(r'owns_any_bypass: wormhole', r'▲拥有§H虫洞§!', string)
        string = re.sub(r'owns_any_bypass: gateway', r'▲拥有§H星门§!', string)
        string = re.sub(r'not_any_owned_planet: \\n※\d*any_tile: \\n※\d*▲拥有', r'△任意星球任意地块都没有', string)
        string = re.sub(r'not_any_owned_planet: \\n※\d*any_tile: \\n※\d*has_blocker: ', r'△任意星球任意地块都没有地块障碍：', string)
        string = re.sub(r'area: engineering\\n※\d*([▲△])', r'\1工程学领袖', string)
        string = re.sub(r'area: physics\\n※\d*([▲△])', r'\1物理学领袖', string)
        string = re.sub(r'area: society\\n※\d*([▲△])', r'\1社会学领袖', string)
        string = re.sub(r'any_neighbor_country: \\n※\d*▲', r'▲任意邻国', string)
        string = re.sub(r'is_ai: §H是§!', r'▲是AI', string)
        string = re.sub(r'has_any_megastructure_in_empire: §H是§!', r'▲国内用有§H巨型建筑§!', string)
        string = re.sub(r'count_starbase_sizes: \\n※\d*starbase_size: §H星([港垒堡])§!\n※\d*count', r'▲§H星\1§!数量', string)
        string = re.sub(r'any_owned_planet: \\n※\d*▲星球类型是(§.*?§!)', r'▲拥有\1类型的星球', string)
        string = re.sub(r'not_any_planet_within_border: \\n※\d*any_pop: \\n※\d*is_sapient: §H否§!',
                        r'△疆域内任意星球都没有§H未开智§!人口',
                        string)
        string = re.sub(r'▲△', r'▲', string)
        string = re.sub(r'№△', r'△', string)
        string = re.sub(r'▲£trigger_no', r'△', string)
        string = re.sub(r'△拥有者没有：\\n.*※\d*is_same_value§H来自§!', r'星系所有者与本的星系不同', string)
        string = re.sub(r'not_has_starbase_size>= starbase_starfortress', r'恒星基地等级未达到§H星堡(或更高)§!', string)
        string = re.sub(r'not_has_starbase_size>= starbase_starport', r'恒星基地等级未达到§H星港(或更高)§!', string)
        string = re.sub(r'graphical_culturefromfrom', r'模型风格与建造者的相同', string)
        string = re.sub(r'拥有者：§H来自§!', r'拥有者设定为§H建造者§!', string)
        string = re.sub(r'set_graphical_cultureroot.from', r'模型风格与§H建造者§!相同', string)
        string = re.sub(r'基准位置fromfrom', r'基准位置：§H当前位置§!', string)
        string = re.sub(r'surveyorFROM', r'调查者：§H建造者§!', string)
        string = re.sub(r'not_is_same_value§H来自§!', r'与§H自己§!不同', string)
        string = re.sub(r'is_same_value§H来自§!', r'与§H自己§!相同', string)
        string = re.sub(r'移除巨型建筑fromfrom\n※\d*№生成该巨型建筑的巨型建筑', r'移除生成该巨型建筑的巨型建筑', string)
        string = re.sub(r'\\n※\d*break§H是§!', r'', string)
        string = re.sub(r'event_target:(.*?)\\n', r'对事件目标\1进行设定：', string)
        string = re.sub(r'fromfrom', r'', string)
        string = re.sub(r'FROM.from .planet.GetName', r'行星名称', string)
        string = re.sub(r'是参战方\\n※\d*whoprev side = attackers', r'以进攻方身份参战', string)
        string = re.sub(r'days = -1', r'持续天数：永久', string)
        string = re.sub(r'days = ', r'持续天数：', string)
        string = re.sub(r'not_years_passed>', r'年数<', string)
        string = re.sub(r'附庸国设定为\\n※\d*who§H无§!', r'取消附庸国状态', string)
        string = re.sub(r'附庸国设定为\\n※\d*who(§H.*?§!)', r'成为\1的附庸国', string)
        string = re.sub(r'加入战争§H来自§!', r'加入§H前者的§!战争', string)
        string = re.sub(r'> @protectorate_tech_threshold', r'>0.4', string)
        string = re.sub(r'< @protectorate_tech_threshold', r'<0.4', string)
        string = re.sub(r'> @protectorate_tech_switch', r'>0.5', string)
        string = re.sub(r'>= starbase_citadel', r'>= §H擎天堡§!', string)
        string = re.sub(r'break§H是§!', r'分支结束', string)
        string = re.sub(r'<div style="margin-left:14px">▲(>= \d*?)</div>'
                        r'<div style="margin-left:14px">▲(< \d*?)</div></div>', r'\1且\2', string)
        # string = re.sub(
        #     r'', r'分支结束', string)

        for count in range(4, 0, -1):
            string = re.sub(r'(:?<div style="margin-left:14px">){'+ str(count) + '}(.*?)(:?</div>){'+ str(count) + '}',
                            r'<div style="margin-left:14px">\2</div>', string)

        string = re.sub(
            r'<div style="margin-left:14px">▲增加(\d*)</div>'
            r'<div style="margin-left:14px">▲星球类型是§H(.*?)§!</div>',
            r'<div style="margin-left:14px">▲如果星球类型是§H\2§!，则概率增加\1</div>',
            string)
        # string = re.sub(r'№如果满足下列条件，则(.*?)<div style="margin-left:14px">([^<])(.*?)</div>',
        #                 r'\2如果\3，则\1', string)
        string = re.sub(r'<div style="margin-left:14px">№如果满足下列条件，则(系数 × \d*)</div>$',
                        r'基础\1', string)

        string = re.sub(r'§[^!](§[^!]*?§!)§!', r'\1', string)
        if string == '№':
            string = ''

        # string = re.sub(r'^<div style="margin-left:14px">(.*?)</div>$', r'\1', string)
        # string = re.sub(r'fail_text:\s(.*?)\\n', r'\1即满足以下条件：\\n', string)
        Danteng.log(string)
        return string

    # 输出xlsx和json
    def save_data(self, data, item_category=None):
        if item_category is None:
            item_category = self.item_category
        # 生成excel数据
        headers = OrderedDict([(item_category, ['_index'])])
        contents = OrderedDict([(item_category, OrderedDict())])
        total_index = 0
        for key, info in data.items():
            if not ('_index' in info):
                total_index += 1
                info['_index'] = total_index
            contents[item_category][key] = info
            for header_name in info.keys():
                if header_name not in headers[item_category]:
                    headers[item_category].append(header_name)
        save_filepath = os.path.join('excel\\' + item_category + '.xlsx')
        save_to_excel(headers, contents, save_filepath)

        # 生成json数据
        cn_json = json.dumps(data, ensure_ascii=False)
        with open('json\\' + item_category + '.json', 'w', encoding='UTF-8') as f:
            f.write(cn_json)

    def processor(self):
        self.data = self.data_processor()
        for name, item in self.data.items():
            if 'prerequisites' in item:
                for index in range(len(item['prerequisites'])):
                    if item['main_category'] not in self.tech_prerequisites_cat:
                        self.tech_prerequisites_cat.append(item['main_category'])
                    if item['prerequisites'][index] not in self.tech_prerequisites:
                        self.tech_prerequisites[item['prerequisites'][index]] = OrderedDict()
                    if item['main_category'] not in self.tech_prerequisites[item['prerequisites'][index]]:
                        self.tech_prerequisites[item['prerequisites'][index]][item['main_category']] = []
                    self.tech_prerequisites[item['prerequisites'][index]][item['main_category']].append(name)
            for key in item:
                if key not in self.base_key_list and key not in self.all_keys:
                    self.all_keys.append(key)
        self.all_data[self.item_category] = self.data

    def get_loc_icon(self):
        temp_list = []
        for name, item in self.i18n_en_map.items():
            sub_list = re.findall(r'£\S*', item)
            for index in range(len(sub_list)):
                if sub_list[index] not in temp_list:
                    temp_list.append(sub_list[index])
        for i in range(len(temp_list)):
            sub_list = re.findall(r'^£[^£|]*', temp_list[i])
            for index in range(len(sub_list)):
                if sub_list[index] not in self.loc_icon:
                    self.loc_icon.append(sub_list[index])

# Abstract methods
    @abstractmethod
    def data_processor(self):
        return OrderedDict()

    @abstractmethod
    def refinery(self):
        return OrderedDict()
