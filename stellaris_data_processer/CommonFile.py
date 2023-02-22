from collections import OrderedDict
import re

from FoolDonkeyAssignment import pdx_resource, pdx_logic, pdx_replace_dict, preprocess_pdx_dict, pdx_modifier, \
    pdx_manual_dict
from danteng import Danteng
from localization import modifier_replace

modifier_list = ['modifier', 'country_modifier', 'assembling_modifier', 'declining_modifier', 'growing_modifier',
                 'self_modifier', 'planet_modifier']
logic_list = ['random_weight', 'weight_modifier', 'ai_weight', 'leader_potential_add', 'species_potential_add',
              'possible', 'weight', 'potential', 'playable', 'ai_wants', 'drop_weight', 'triggered_planet_modifier']
aux_keys = ['file', 'key', 'main_category', 'version', 'zhcn_name', 'en_name', 'zhcn_desc', 'en_desc', 'icon',
            'custom_tooltip', 'description', 'resources', 'prerequisites']

PREFIX_STR = '☆'
SUFFIX_STR = '★'


class CommonFile:
    modifier_keys = []
    variables = OrderedDict()
    all_data = OrderedDict()
    icon_dict = OrderedDict()

    def __init__(self, raw_file, category, all_loc, version, main_data=True):
        self.data = OrderedDict()
        self.category = category
        self.all_loc = all_loc
        self.version = version
        self.main_data = main_data
        self.debug = []
        self.refined = OrderedDict()
        self.keys = []

        self.merge(raw_file)
        self.assign()
        self.read_keys()
        self.process()
        self.post_process()
        self.all_data[category] = self.data
        z = 1

    def merge(self, raw_file):
        for file_name in raw_file:
            if len(self.refined) == 0:
                for name in raw_file[file_name]:
                    raw_file[file_name][name]['file'] = file_name
                self.refined = raw_file[file_name]
            else:
                for name in raw_file[file_name]:
                    if name in self.refined and type(self.refined[name]) == list:
                        for i in range(len(self.refined[name])):
                            raw_file[name][i]['file'] = file_name
                            self.refined[name].append(raw_file[name][i])
                    elif name[0] == '@':
                        self.variables[name] = raw_file[file_name][name]
                    else:
                        raw_file[file_name][name]['file'] = file_name
                        self.refined[name] = raw_file[file_name][name]

    def assign(self):
        self.loop_variables(self.refined)

    def loop_variables(self, item):
        for name in item:
            if type(item[name]) == str:
                if '@' in item[name]:
                    item[name] = self.assign_variables(item[name])
            elif type(item[name]) == list:
                for i in range(len(item[name])):
                    if type(item[name][i]) == str:
                        if '@' in item[name][i]:
                            item[name][i] = self.assign_variables(item[name][i])
                    else:
                        self.loop_variables(item[name][i])
            elif isinstance(item[name], dict):
                self.loop_variables(item[name])

    def assign_variables(self, item):
        found = re.findall(r'(@.*?)\s', item)
        if len(found) > 1:
            z = 11
        elif len(found) == 1:
            return self.replace_variables(item, found[0])
        else:
            return self.replace_variables(item, item[item.find('@'):])
        return item

    def replace_variables(self, item, var):
        if var in self.variables:
            repl = self.variables[var]
            return item.replace(var, repl)
        elif '@event_target' not in var:
            z = 11
        return item

    def process(self):
        for name in self.refined:
            item = OrderedDict()
            raw = self.refined[name]
            item['key'] = name
            if self.main_data:
                item['main_category'] = self.category
                item['version'] = self.version
                item['zhcn_name'] = self.localise(name, 'cn')[0]
                item['en_name'] = self.localise(name, 'en')[0]
                zhcn_desc = self.localise(name + '_desc', 'cn')
                en_desc = self.localise(name + '_desc', 'en')
                item['zhcn_desc'] = zhcn_desc[0]
                item['en_desc'] = en_desc[0]
                if not en_desc[1]:
                    zhcn_desc = self.localise('SUBJECT_DESC_' + name, 'cn')
                    en_desc = self.localise('SUBJECT_DESC_' + name, 'en')
                    if en_desc[1]:
                        item['zhcn_desc'] = zhcn_desc[0]
                        item['en_desc'] = en_desc[0]
            item.update(self.analysis(raw))
            self.data[name] = item

    def read_keys(self):
        for name in self.refined:
            for key in self.refined[name]:
                if key not in self.keys and key not in modifier_list and key not in logic_list and key not in aux_keys:
                    self.keys.append(key)

    def post_process(self):
        i = 0
        for name in self.data:
            self.data[name]['_index'] = i
            i += 1

    def split_list(self, raw, processed, key, name_cn='', name_en=''):
        if key in raw:
            if type(raw[key]) == str:
                if raw[key] == 'all':
                    processed[name_cn] = self.localise('ALL', 'cn')[0]
                    processed[name_en] = self.localise('ALL', 'en')[0]
                    return
                else:
                    raise Exception('DataException:' + raw[key])
            elif len(raw[key]) > 1:
                for i in range(len(raw[key])):
                    processed[key][i] = raw[key][i].replace('"', '')
                z = 4
            else:
                processed[key] = raw[key][0].split(' ')
            if name_cn != '':
                processed[name_cn] = []
                processed[name_en] = []
                for i in range(len(processed[key])):
                    processed[name_cn].append(self.localise(processed[key][i], 'cn')[0])
                    processed[name_en].append(self.localise(processed[key][i], 'en')[0])

    # For implement
    def analysis(self, raw):
        processed = OrderedDict()
        processed.update(raw)
        if 'description' in raw:
            processed['description'] = raw['description'].replace('"', '')
            processed['zhcn_more_desc'] = self.localise(processed['description'], 'cn')[0]
            processed['en_more_desc'] = self.localise(processed['description'], 'en')[0]
        if 'tags' in raw:
            instruction = ''
            for tag in raw['tags']:
                temp = self.localise(tag, 'cn')
                instruction += temp[0] + '\\n'
                if not temp[1]:
                    z = 7
            processed['instruction'] = instruction[0:-2]
        if 'custom_tooltip' in raw:
            if type(raw['custom_tooltip']) == str:
                processed['zhcn_custom'] = self.localise
                processed['en_custom'] = self.localise(raw['custom_tooltip'], 'en')[0]
            elif type(raw['custom_tooltip']) == list:
                for i in range(len(raw['custom_tooltip'])):
                    if 'text' in raw['custom_tooltip'][i]:
                        processed['custom_tooltip'][i]['zhcn'] = self.localise(raw['custom_tooltip'][i]['text'], 'cn'
                                                                               )[0]
                        processed['custom_tooltip'][i]['en'] = self.localise(raw['custom_tooltip'][i]['text'], 'en')[0]
                    elif 'fail_text' in raw['custom_tooltip'][i]:
                        processed['custom_tooltip'][i]['zhcn'] = self.localise(raw['custom_tooltip'][i]['fail_text'],
                                                                               'cn')[0]
                        processed['custom_tooltip'][i]['en'] = self.localise(raw['custom_tooltip'][i]['fail_text'],
                                                                             'en')[0]
            elif 'text' in raw:
                processed['custom_tooltip']['zhcn'] = self.localise(raw['custom_tooltip']['text'], 'cn')[0]
                processed['custom_tooltip']['en'] = self.localise(raw['custom_tooltip']['text'], 'en')[0]
            elif 'fail_text' in raw:
                processed['custom_tooltip']['zhcn'] = self.localise(raw['custom_tooltip']['fail_text'], 'cn')[0]
                processed['custom_tooltip']['en'] = self.localise(raw['custom_tooltip']['fail_text'], 'en')[0]
            else:
                z = 5
        if 'icon' in raw:
            if raw['icon'] in self.icon_dict:
                if 'textureFile' in self.icon_dict[raw['icon']]:
                    processed['icon'] = self.icon_dict[raw['icon']]['textureFile'].replace('"', '').split(
                        '/')[-1].split('.')[0]
                elif 'texturefile' in self.icon_dict[raw['icon']]:
                    processed['icon'] = self.icon_dict[raw['icon']]['texturefile'].replace('"', '').split(
                        '/')[-1].split('.')[0]
                else:
                    z = 6
                z = 7
            else:
                processed['icon'] = raw['icon'].replace('"', '').split('/')[-1].split('.')[0]
                z = 8
        if 'resources' in raw:
            z = 6
            if 'cost' in raw['resources']:
                processed['cost_detail'] = ''
                if isinstance(raw['resources']['cost'], list):
                    for case_id in range(len(raw['resources']['cost'])):
                        sub_case = raw['resources']['cost'][case_id]
                        if 'trigger' in sub_case:
                            processed['cost_detail'] += '如果' + self.logic(sub_case, 'trigger') + '\n则花费'
                        else:
                            processed['cost_detail'] += '默认则花费'
                        for sub_name in sub_case:
                            if sub_name != 'trigger':
                                processed['cost_detail'] += '£' + sub_name + sub_case[sub_name]
                        processed['cost_detail'] += '\n'
                    z = 8
                else:
                    for res, cost_value in raw['resources']['cost'].items():
                        processed['cost_detail'] += '£' + res + cost_value
                z = 9
        if 'cost' in raw:
            z = 7
        if 'prerequisites' in raw:
            for i in range(len(raw['prerequisites'])):
                processed['prerequisites'][i] = raw['prerequisites'][i].replace('"', '')

        for i in range(len(modifier_list)):
            key = modifier_list[i]
            if key in raw:
                processed['zhcn_' + key], processed['en_' + key] = self.modifier(raw, key)
        for i in range(len(logic_list)):
            key = logic_list[i]
            if key in raw:
                processed['zhcn_' + key] = self.logic(raw, key)
        return processed

    # Localization
    def localise(self, item, lang='cn', empty=False):
        if type(item) != str:
            Danteng.log('错误：文本传入参数不是字符串')
            return '', False
        prefix = ['mod_', 'pft_', 'personality_type_', 'personality_', 'casus_belli_', 'SUBJECT_', 'sm_', 'country_']
        surfix = ['_trigger', '_mult']
        found_it = False
        loc_str = ''
        item = item.replace('"', '')
        if item in self.all_loc[lang]:
            loc_str = self.all_loc[lang][item]
            found_it = True
        elif item + '_trigger' in self.all_loc[lang]:
            loc_str = self.all_loc[lang][item + '_trigger']
            found_it = True
        elif item in pdx_replace_dict:
            loc_str, found_it = self.localise(pdx_replace_dict[item], lang)
        elif item in pdx_manual_dict and lang in pdx_manual_dict[item]:
            loc_str = pdx_manual_dict[item][lang]
            found_it = True
        else:
            for i in range(len(prefix)):
                compound = prefix[i] + item
                if compound in self.all_loc[lang]:
                    loc_str = self.all_loc[lang][compound]
                    found_it = True
                    break
            if not found_it:
                for i in range(len(surfix)):
                    compound = item + surfix[i]
                    if compound in self.all_loc[lang]:
                        loc_str = self.all_loc[lang][compound]
                        found_it = True
                        break
        if not found_it:
            if item in self.all_loc['en']:  # 遗漏时占位
                loc_str, found_it = self.localise(item, 'en')
            elif empty:
                loc_str = ''
                found_it = True
            else:
                loc_str = item
        return loc_str, found_it
    # 'hive_mind', 'machine_intelligence', 'corporate'

    def modifier(self, raw_dict, key):
        return self.modifier_processor(raw_dict[key], 'cn'), self.modifier_processor(raw_dict[key], 'en')

    def modifier_processor(self, raw_dict, lang='cn'):
        name_str = ''
        if 'description' in raw_dict:
            name_str = self.localise(raw_dict['description'], lang)[0]
            if 'description_parameters' in raw_dict:
                for item in raw_dict['description_parameters']:
                    value = raw_dict['description_parameters'][item]
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
        if type(raw_dict) == str:
            key = raw_dict.replace('"', '')
            name_str = self.localise(key, lang)[0]
            name_str.strip()
            if '@' in raw_dict:
                z = 3
            Danteng.log(name_str)
            return name_str
        elif type(raw_dict) == list:
            for i in range(len(raw_dict)):
                name_str += self.localise(raw_dict[i], lang)[0] + '\\n'
                if '@' in raw_dict[i]:
                    z = 3
            return name_str[0:-2]
        for key, value in raw_dict.items():
            if key in pdx_replace_dict:
                key = pdx_replace_dict[key]
            loc_str = self.localise(key, lang)
            if loc_str[1]:
                name_str += loc_str[0] + '：'

            temp_str = ''
            if key == 'custom_tooltip':
                name_str = self.localise(value, lang)[0]
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
        find = re.findall(r'\$.*?\$', name_str)
        if find:
            for item in find:
                find_key = item[1:-1]
                name_str = name_str.replace(item, self.localise(find_key, lang)[0])
        name_str.strip()
        Danteng.log(name_str[0:-2])
        return name_str[0:-2]

    def logic_it(self, raw, processed, key, new_key):
        if key in raw:
            processed[new_key] = self.logic(raw, key)

    def logic(self, raw_dict, key, name=''):
        logic_str = self.logic_processor(raw_dict[key])
        logic_str = re.sub(r'\\n(\s*?)\\n', r'\\n\1〓--------------\\n', logic_str[0])
        if logic_str == '':
            return logic_str
        elif logic_str[0] == '№':
            logic_str = logic_str[1:]
        logic_str = modifier_replace(logic_str)
        prefix_count = len(re.findall(PREFIX_STR, logic_str))
        suffix_count = len(re.findall(SUFFIX_STR, logic_str))
        if prefix_count != suffix_count:
            z = 5
        if name == '':
            if 'zhcn_name' in raw_dict:
                Danteng.log('\n' + raw_dict['zhcn_name'] + '的logic：' + logic_str)
            else:
                Danteng.log('\n' + '未知的' + key + '的logic：' + logic_str)
        else:
            Danteng.log('\n' + name + '的logic：' + logic_str)
        return logic_str

    @staticmethod
    def strange_flags(non_flag, positive):
        if non_flag:
            return '№'
        else:
            if positive:
                return '▲'
            else:
                return '△'

    def logic_processor(self, logic_item, deep=False, name='', flag_not=False, positive=True, is_list_item=False,
                        more_dict={}, has_text=False):
        logic_str = ''
        temp_str = ''
        start_str = ''
        end_str = ''
        has_var = False
        non_flag = False
        if deep:
            start_str = PREFIX_STR
            end_str = SUFFIX_STR
        if flag_not:
            name = 'not_' + name
        positive = positive ^ flag_not  # flag_not和positive同真为假，同假为真，恰好符合异或
        if name == 'NOT' or name == 'not':
            positive = not (positive ^ False)

        elif name in pdx_resource:
            name_str = '£' + pdx_resource[name] + '§H' + self.localise(name, 'cn')[0] + '§!'
            logic_str += temp_str + name_str

        elif 'scripted_triggers' in self.all_data and name in self.all_data['scripted_triggers']:
            if 'zhcn_name' in self.all_data['scripted_triggers'][name] and self.all_data['scripted_triggers'][name][
                                                                            'zhcn_name'] != '':
                logic_str += temp_str + self.all_data['scripted_triggers'][name]['zhcn_name']
            else:
                z = 5

        elif name in pdx_logic:
            name_str = self.localise(pdx_logic[name]['value'], 'cn')[0]
            if 'positive' in pdx_logic[name]:
                positive = not (positive ^ pdx_logic[name]['positive'])
            else:
                non_flag = True
            if re.findall(r'\$.*?\$', name_str):
                has_var = True
            temp_str += self.strange_flags(non_flag, positive)
            logic_str += temp_str + name_str

        elif is_list_item:
            temp_str += self.strange_flags(non_flag, positive)
        elif name == '':
            temp_str += temp_str + self.strange_flags(non_flag, positive)

        else:
            refined_name = self.localise(name, 'cn')
            if re.findall(r'\$.*?\$', refined_name[0]):
                has_var = True
            logic_str += temp_str + refined_name[0]
            if not refined_name[1]:
                if name not in self.debug:
                    self.debug.append(name)
                z = 5

        if isinstance(logic_item, str):
            logic_item = logic_item.replace('"', '')
            if logic_item in pdx_resource:
                logic_item = '£' + pdx_resource[logic_item] + '§H' + self.localise(logic_item, 'cn')[0] + '§!'
            elif logic_item in pdx_logic:
                logic_item = '§H' + self.localise(pdx_logic[logic_item]['value'], 'cn')[0] + '§!'
            logic_head, found_it = self.localise(logic_item, 'cn')
            if found_it:
                logic_item = '§H' + logic_head + '§!'
            elif len(more_dict) != 0 and logic_item in more_dict and 'zhcn_name' in more_dict[logic_item]:
                logic_item = '§H' + more_dict[logic_item]['zhcn_name'] + '§!'
            if has_var:
                logic_str = re.sub(r'\$.*?\$', logic_item, logic_str)
                start_str = ''
                end_str = ''
            else:
                if is_list_item:
                    logic_str += temp_str + logic_item
                else:
                    logic_str += logic_item
        elif isinstance(logic_item, dict):
            if 'text' in logic_item:
                has_text = True
                logic_item['text'] = logic_item['text'].replace('"', '')
                if logic_item['text'] in self.all_loc['cn']:
                    logic_str = temp_str + self.localise(logic_item['text'], 'cn')[0].replace('§R', '§W')
                elif logic_item['text'] in self.all_loc['en']:
                    logic_str = temp_str + self.all_loc['en'][logic_item['text']].replace('§R', '§W')
                else:
                    Danteng.log("————" + logic_item['text'] + '没找到')
                    logic_str = temp_str + logic_item['text']
            elif 'fail_text' in logic_item:
                has_text = True
                logic_item['fail_text'] = logic_item['fail_text'].replace('"', '')
                if logic_item['fail_text'] in self.all_loc['cn']:
                    if '£trigger_no' in logic_item['fail_text']:
                        logic_str = temp_str + self.localise(logic_item['fail_text'], 'cn')[0]
                    else:
                        logic_str = temp_str + '△' + self.localise(logic_item['fail_text'], 'cn')[0]
                elif logic_item['fail_text'] in self.all_loc['en']:
                    logic_str = temp_str + '△' + self.all_loc['en'][logic_item['fail_text']]
                else:
                    Danteng.log("————" + logic_item['fail_text'] + '没找到')
                    logic_str = temp_str + logic_item['fail_text']
            elif 'custom_tooltip' in logic_item and isinstance(logic_item['custom_tooltip'], str):
                has_text = True
                logic_item['custom_tooltip'] = logic_item['custom_tooltip'].replace('"', '')
                if logic_item['custom_tooltip'] in self.all_loc['cn']:
                    logic_str = temp_str + self.localise(logic_item['custom_tooltip'], 'cn')[0].replace('§R', '§W')
                elif logic_item['custom_tooltip'] in self.all_loc['en']:
                    logic_str = temp_str + self.all_loc['en'][logic_item['custom_tooltip']].replace('§R', '§W')
                else:
                    Danteng.log("————" + logic_item['custom_tooltip'] + '没找到')
                    logic_str = temp_str + logic_item['custom_tooltip']
            elif name == 'NOT':
                for item in logic_item:
                    logic_str += self.logic_processor(logic_item[item], deep, item, True, positive=positive,
                                                      more_dict=more_dict)[0]
            else:
                for item in logic_item:
                    if has_var:
                        logic_str = re.sub(r'\$.*?\$', '', logic_str)
                    logic_str += self.logic_processor(logic_item[item], True, item, positive=positive,
                                                      more_dict=more_dict)[0]
        elif isinstance(logic_item, list):
            if has_var:
                logic_str = re.sub(r'\$.*?\$', '', logic_str)
                # start_str = ''
                # end_str = ''
            list_str = ''
            for i in range(len(logic_item)):
                list_str += self.logic_processor(logic_item[i], False, positive=positive, is_list_item=True,
                                                 more_dict=more_dict)[0] + '\\n'
            logic_str += list_str[0:-2]
        else:
            Danteng.log('这行没处理:\t\t' + str(logic_item))
        logic_str = start_str + logic_str + end_str
        return logic_str, has_text

    def replace(self, text):
        text.replace('★\\n☆', '')

    def get_data(self):
        return self.data

    def upload(self):
        z = 1
