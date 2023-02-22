# 处理所有Modifier相关的内容
# 单独列出一个属性来存储描述
import re

from danteng import Danteng
from FoolDonkeyAssignment import pdx_replace_dict, pdx_logic, pdx_dict_detail, \
    pdx_logic_word, preprocess_pdx_dict, pdx_resource
from FoolDonkeyAssignment import pdx_modifier
from utilities import zhcn


def modifier_processor(modifier_dict, i18n_zhcn_map, i18n_en_map):
    name_str = ''
    if 'description' in modifier_dict:
        name_str = i18n_zhcn_map[modifier_dict['description']]
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
        if key in i18n_zhcn_map:
            name_str = i18n_zhcn_map[key]
        elif key.upper in i18n_zhcn_map:
            name_str = i18n_zhcn_map[key.upper()]
        elif 'country_' + key in i18n_zhcn_map:
            name_str = i18n_zhcn_map['country_' + key]
        elif key in pdx_replace_dict:
            if pdx_replace_dict[key] in i18n_zhcn_map:
                name_str = i18n_zhcn_map[pdx_replace_dict[key]]
            else:
                name_str = i18n_en_map[pdx_replace_dict[key]]
        elif key in i18n_en_map:
            name_str = i18n_en_map[key]
        elif key.upper in i18n_en_map:
            name_str = i18n_en_map[key.upper()]
        elif 'country_' + key in i18n_en_map:
            name_str = i18n_en_map['country_' + key]
        else:
            name_str = key
        name_str.strip()
        Danteng.log(name_str)
        return name_str
    for key, value in modifier_dict.items():
        # mod_key = 'MOD_' + key
        if key in i18n_zhcn_map:
            name_str += i18n_zhcn_map[key] + '：'
        elif key.upper in i18n_zhcn_map:
            name_str += i18n_zhcn_map[key.upper()] + '：'
        elif 'country_' + key in i18n_zhcn_map:
            name_str += i18n_zhcn_map['country_' + key] + '：'
        elif key[-5:] == '_mult' and key[0:-5] in i18n_zhcn_map:
            name_str += i18n_zhcn_map[key[0:-5]] + '：'
        elif key in pdx_replace_dict:
            name_str += i18n_zhcn_map[pdx_replace_dict[key]] + '：'
        elif key in i18n_en_map:
            name_str += i18n_en_map[key] + '：'
        elif key.upper in i18n_en_map:
            name_str += i18n_en_map[key.upper()] + '：'
        elif 'country_' + key in i18n_en_map:
            name_str += i18n_en_map['country_' + key] + '：'
        elif key[-5:] == '_mult' and key[0:-5] in i18n_en_map:
            name_str += i18n_en_map[key[0:-5]] + '：'
        elif key in pdx_replace_dict:
            name_str += i18n_en_map[pdx_replace_dict[key]] + '：'
        else:
            name_str = key

        temp_str = ''
        if type(value) == str and value != '':
            if value == 'yes':
                temp_str = '▲'
            elif value == 'no':
                temp_str = '△'
            else:
                num = float(value)
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
            if find_key in i18n_zhcn_map:
                name_str = name_str.replace(item, i18n_zhcn_map[find_key])
            elif find_key in i18n_en_map:
                name_str = name_str.replace(item, i18n_en_map[find_key])
    name_str.strip()
    Danteng.log(name_str[0:-2])
    return name_str[0:-2]


def choice(item, i18n_zhcn_map, i18n_en_map, depth=0):
    desc = ''
    temp_str = ''
    if depth > 0:
        temp_str = '※' + str(depth * 14)
    if 'if' in item:
        if 'limit' in item['if']:
            desc += '\\n如果满足条件§H'
            for name, value in item['if']['limit'].items():
                if name in i18n_zhcn_map:
                    i18n_name = i18n_zhcn_map[name]
                elif name in i18n_en_map:
                    i18n_name = i18n_en_map[name]
                else:
                    i18n_name = name
                desc += temp_str + i18n_name + value
            desc += '§!：'
        if 'custom_tooltip' in item['if']:
            name = item['if']['custom_tooltip']
            if name in i18n_zhcn_map:
                i18n_name = i18n_zhcn_map[name]
            elif name in i18n_en_map:
                i18n_name = i18n_en_map[name]
            else:
                i18n_name = name
            desc += i18n_name
        if 'else' in item['if']:
            desc += '\\n§L不满足上述条件时：§E\\n' + choice(item['if']['else'], i18n_zhcn_map, i18n_en_map, depth + 1)
            if 'custom_tooltip' in item['if']['else']:
                name = item['if']['custom_tooltip']
                if name in i18n_zhcn_map:
                    i18n_name = i18n_zhcn_map[name]
                elif name in i18n_en_map:
                    i18n_name = i18n_en_map[name]
                else:
                    i18n_name = name
                desc += i18n_name
    return desc


def logic_processor(logic_item, i18n_zhcn_map, i18n_en_map, depth=0, name='', flag_not=False, positive=True,
                    is_list_item=False, more_dict={}, has_text=False):
    logic_str = ''
    temp_str = ''
    has_var = False
    non_flag = False
    if name == '':
        depth = depth - 1
    if depth > 0:
        temp_str = '※' + str(depth * 14)

    if flag_not:
        name = 'not_' + name

    positive = positive ^ flag_not  # flag_not和positive同真为假，同假为真，恰好符合异或
    if name == 'NOT':
        positive = not (positive ^ False)
    # elif name == '':
    #     pass
    elif name in pdx_resource:
        name_str = '£' + pdx_resource[name] + '§H' + i18n_zhcn_map[name] + '§!'
        logic_str += temp_str + name_str
    elif name in pdx_logic:
        name_str = pdx_logic[name]['value']
        if 'positive' in pdx_logic[name]:
            positive = not (positive ^ pdx_logic[name]['positive'])
        else:
            non_flag = True

        if re.findall(r'\$.*?\$', name_str):
            has_var = True

        if non_flag:
            temp_str += '№'
        else:
            if positive:
                temp_str += '▲'
            else:
                temp_str += '△'

        logic_str += temp_str + name_str
    elif name == '':
        if non_flag:
            temp_str = '※' + str(depth * 14 + 14) + '№'
        else:
            if positive:
                temp_str = '※' + str(depth * 14 + 14) + '▲'
            else:
                temp_str = '※' + str(depth * 14 + 14) + '△'

    # elif name[0:4] == 'has_' or name[0:3] == 'is_' or name[0:8] == 'not_has_' or name[0:7] == 'not_is_':
    #     logic_str += name + '：'
    else:
        logic_str += temp_str + name

    if isinstance(logic_item, str):
        logic_item = logic_item.replace('"', '')
        if logic_item in pdx_resource:
            logic_item = '£' + pdx_resource[logic_item] + '§H' + i18n_zhcn_map[logic_item] + '§!'
        elif logic_item in pdx_logic:
            logic_item = '§H' + pdx_logic[logic_item]['value'] + '§!'
        elif logic_item in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map[logic_item] + '§!'
        elif ('pft_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['pft_' + logic_item] + '§!'
        elif ('personality_type_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['personality_type_' + logic_item] + '§!'
        elif ('personality_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['personality_' + logic_item] + '§!'
        elif ('casus_belli_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['casus_belli_' + logic_item] + '§!'
        elif ('SUBJECT_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['SUBJECT_' + logic_item] + '§!'
        elif ('sm_' + logic_item) in i18n_zhcn_map:
            logic_item = '§H' + i18n_zhcn_map['sm_' + logic_item] + '§!'
        elif logic_item in i18n_en_map:
            logic_item = '§H' + i18n_en_map[logic_item] + '§!'
        elif ('pft_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['pft_' + logic_item] + '§!'
        elif ('personality_type_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['personality_type_' + logic_item] + '§!'
        elif ('personality_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['personality_' + logic_item] + '§!'
        elif ('casus_belli_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['casus_belli_' + logic_item] + '§!'
        elif ('SUBJECT_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['SUBJECT_' + logic_item] + '§!'
        elif ('sm_' + logic_item) in i18n_en_map:
            logic_item = '§H' + i18n_en_map['sm_' + logic_item] + '§!'
        elif len(more_dict) != 0 and logic_item in more_dict and 'zhcn_name' in more_dict[logic_item]:
            logic_item = '§H' + more_dict[logic_item]['zhcn_name'] + '§!'
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
            if logic_item['text'] in i18n_zhcn_map:
                logic_str = temp_str + i18n_zhcn_map[logic_item['text']].replace('§R', '§W')
            elif logic_item['text'] in i18n_en_map:
                logic_str = temp_str + i18n_en_map[logic_item['text']].replace('§R', '§W')
            else:
                Danteng.log("————" + logic_item['text'] + '没找到')
                logic_str = temp_str + logic_item['text']
        elif 'fail_text' in logic_item:
            has_text = True
            logic_item['fail_text'] = logic_item['fail_text'].replace('"', '')
            if logic_item['fail_text'] in i18n_zhcn_map:
                if '£trigger_no' in logic_item['fail_text']:
                    logic_str = temp_str + i18n_zhcn_map[logic_item['fail_text']]
                else:
                    logic_str = temp_str + '△' + i18n_zhcn_map[logic_item['fail_text']]
            elif logic_item['fail_text'] in i18n_en_map:
                logic_str = temp_str + '△' + i18n_en_map[logic_item['fail_text']]
            else:
                Danteng.log("————" + logic_item['fail_text'] + '没找到')
                logic_str = temp_str + logic_item['fail_text']
        elif 'custom_tooltip' in logic_item and isinstance(logic_item['custom_tooltip'], str):
            has_text = True
            logic_item['custom_tooltip'] = logic_item['custom_tooltip'].replace('"', '')
            if logic_item['custom_tooltip'] in i18n_zhcn_map:
                logic_str = temp_str + i18n_zhcn_map[logic_item['custom_tooltip']].replace('§R', '§W')
            elif logic_item['custom_tooltip'] in i18n_en_map:
                logic_str = temp_str + i18n_en_map[logic_item['custom_tooltip']].replace('§R', '§W')
            else:
                Danteng.log("————" + logic_item['custom_tooltip'] + '没找到')
                logic_str = temp_str + logic_item['custom_tooltip']
        elif name == 'NOT':
            for item in logic_item:
                logic_str += '\\n' + \
                            logic_processor(logic_item[item], i18n_zhcn_map, i18n_en_map, depth, item, True,
                                            positive=positive, more_dict=more_dict)[0]
        else:
            depth += 1
            for item in logic_item:
                logic_str += '\\n' + logic_processor(logic_item[item], i18n_zhcn_map, i18n_en_map, depth,
                                                                item, positive=positive, more_dict=more_dict)[0]
    elif isinstance(logic_item, list):
        depth += 1
        if has_var:
            logic_str = re.sub(r'\$.*?\$', '', logic_str)
        for i in range(len(logic_item)):
            logic_str += '\\n\t' + \
                        logic_processor(logic_item[i], i18n_zhcn_map, i18n_en_map, depth, positive=positive,
                                        is_list_item=True, more_dict=more_dict)[0]
    else:
        Danteng.log('这行没处理:\t\t' + str(logic_item))
    return logic_str, has_text


def possible_processor(modifier_dict, i18n_zhcn_map, i18n_en_map, flag=True, title='', depth=0):
    name_str = ''
    if depth != 0:
        name_str = '※' + str(depth * 14)
    if type(modifier_dict) == list:
        name_str = ''
        for i in range(len(modifier_dict)):
            name_str += possible_processor(modifier_dict[i], i18n_zhcn_map, i18n_en_map, flag, title, depth)
    elif type(modifier_dict) != str:
        if 'text' in modifier_dict:
            if flag:
                temp_str = '▲'
            else:
                temp_str = '△'
            i18n_str = zhcn(modifier_dict['text'].replace('"', ''), i18n_zhcn_map, i18n_en_map)[0]
            name_str += temp_str + i18n_str + '\\n'
        elif 'fail_text' in modifier_dict:
            if flag:
                temp_str = '▲'
            else:
                temp_str = '△'
            i18n_str = zhcn(modifier_dict['fail_text'].replace('"', ''), i18n_zhcn_map, i18n_en_map)[0]
            name_str += temp_str + i18n_str + '\\n'
        else:
            if title in pdx_logic_word:
                if title != 'NOR':
                    temp_str = '▲'
                else:
                    temp_str = '△'
                name_str += temp_str + pdx_logic[title]['value'] + '\\n'
                depth = 1
            for key, value in modifier_dict.items():
                if key == 'NOR':
                    flag = False
                name_str += possible_processor(value, i18n_zhcn_map, i18n_en_map, flag, key, depth)
    else:
        modifier_dict = modifier_dict.replace('"', '')
        if flag:
            temp_str = '▲拥有'
        else:
            temp_str = '△不接受'

        if modifier_dict in pdx_logic:
            temp_str += '§Y' + pdx_logic[modifier_dict]['value'] + '§!' + '\\n'
        elif modifier_dict in i18n_zhcn_map:
            temp_str += '§Y' + i18n_zhcn_map[modifier_dict] + '§!' + '\\n'
        elif modifier_dict in i18n_en_map:
            temp_str += '§Y' + i18n_en_map[modifier_dict] + '§!' + '\\n'

        name_str += temp_str
    name_str.strip()
    Danteng.log(name_str)
    return name_str


def authorities_detail_processor(value, i18n_zhcn_map, i18n_en_map):
    detail_str = ''
    for item in pdx_dict_detail:
        if item in value:
            if value[item] == 'no':
                detail_str += '△' + pdx_dict_detail[item]['deny'] + pdx_dict_detail[item][
                    'value'] + '\\n'
            elif value[item] == 'yes':
                detail_str += '▲' + pdx_dict_detail[item]['value'] + '\\n'
            elif value[item] in i18n_zhcn_map:
                detail_str += '▲' + pdx_dict_detail[item]['value'] + i18n_zhcn_map[
                    value[item]] + '\\n'
            elif ('auth_' + value[item]) in i18n_zhcn_map:
                detail_str += '▲' + pdx_dict_detail[item]['value'] + i18n_zhcn_map[
                    'auth_' + value[item]] + '\\n'
            elif value[item] in i18n_en_map:
                detail_str += '▲' + pdx_dict_detail[item]['value'] + i18n_en_map[
                    value[item]] + '\\n'
            elif ('auth_' + value[item]) in i18n_en_map:
                detail_str += '▲' + pdx_dict_detail[item]['value'] + i18n_en_map[
                    'auth_' + value[item]] + '\\n'
            else:
                detail_str += '▲' + pdx_dict_detail[item]['value'] + value[item] + '\\n'
    Danteng.log(detail_str)
    return detail_str


def logic_it(logic_name, value, i18n_zhcn_map, i18n_en_map, logic_title, more_dict, name_str=''):
    # if logic_name in value:
    logic_str = logic_processor(value[logic_name], i18n_zhcn_map, i18n_en_map, 0, '§E' + logic_title + '§!',
                                more_dict=more_dict)
    logic_str = re.sub(r'\\n(\s*?)\\n', r'\\n\1〓--------------\\n', logic_str[0])
    if logic_str[0] == '№':
        logic_str = logic_str[1:]
    logic_str = modifier_replace(logic_str)
    if name_str == '':
        Danteng.log('\n' + value['zhcn_name'] + '的logic：' + logic_str)
    else:
        Danteng.log('\n' + name_str + '的logic：' + logic_str)
    value[logic_name + '_logic'] = logic_str


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
    string = re.sub(r'not_any_planet_within_border: \\n※\d*any_pop: \\n※\d*is_sapient: §H否§!', r'△疆域内任意星球都没有§H未开智§!人口',
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

    if string == '№':
        string = ''

    # string = re.sub(r'fail_text:\s(.*?)\\n', r'\1即满足以下条件：\\n', string)
    Danteng.log(string)
    return string
