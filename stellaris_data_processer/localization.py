import re
from FoolDonkeyAssignment import pdx_replace_dict
from danteng import Danteng


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