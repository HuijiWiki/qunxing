import json
import re
from collections import OrderedDict

import os

import requests

from FoolDonkeyAssignment import pdx_logic, pdx_resource
from SaveToExcel import save_to_excel
from danteng import Danteng
from modifier_processor import modifier_processor, logic_it, possible_processor, authorities_detail_processor, \
    modifier_replace, choice
from paradox_parser import ParadoxParser
from utilities import zhcn, var_processor


# 处理common文件夹的内容
# 每个子文件夹单独处理
def common_processor(base_path, add_path, item_category, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var,
                     is_common=True):
    if is_common:
        common_path = base_path + 'common\\'
    else:
        common_path = base_path
    common_data = dict()
    all_var = all_global_var
    for filename in os.listdir(os.path.join(common_path, add_path)):
        if filename[-4:] == '.txt':
            pp = ParadoxParser(os.path.join(common_path, add_path, filename), item_category)
            [data, global_var] = pp.get_data()
            all_var.update(global_var)
            common_data.update(data)
    if len(all_var) != 0:
        var_processor(common_data, all_var)
    add_important_keys(common_data, item_category, i18n_zhcn_map, i18n_en_map, version, icons)
    return common_data


def text_processor(base_path, filename, item_category):
    common_path = base_path + 'common\\'
    common_data = dict()
    pp = ParadoxParser(os.path.join(common_path, filename), item_category)
    data = pp.get_data()[0]
    common_data.update(data)
    return common_data


def scripted_variables_processor(base_path):
    item_category = 'global'
    common_path = base_path + 'common\\'
    filename = 'scripted_variables\\00_scripted_variables.txt'
    pp = ParadoxParser(os.path.join(common_path, filename), item_category)
    all_global_var = pp.get_data()[1]
    return all_global_var


# icons 图标
def interface_processor(base_path):
    item_category = 'interface'
    icons_data = OrderedDict()
    icon_list = ['icons', 'eventpictures']
    for name in icon_list:
        path = 'icons\\'+ name + '.gfx'
        icons = text_processor(base_path, path, item_category)
        icons_data.update(icons_refinery(icons))
    save_data(item_category, icons_data)
    return icons_data


def event_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'events'
    events = common_processor(base_path, 'events', item_category, i18n_zhcn_map, i18n_en_map, version,
                              icons, all_global_var, False)
    events_data = events_refinery(events, i18n_zhcn_map, i18n_en_map, icons)
    save_data(item_category, events_data)
    return events_data


# Megastructures 巨型建筑
def megastructures_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'megastructures'
    megastructures = common_processor(base_path, 'megastructures', item_category, i18n_zhcn_map, i18n_en_map, version,
                                      icons, all_global_var)
    megastructures_data = megastructures_refinery(megastructures, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, megastructures_data)
    return megastructures_data


# section_templates 区块
def section_templates_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'section_templates'
    section_templates = common_processor(base_path, 'section_templates', item_category, i18n_zhcn_map, i18n_en_map,
                                         version, icons, all_global_var)
    section_templates_data = section_templates_refinery(section_templates, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, section_templates_data)
    return section_templates_data


# component_sets 组件图标
def component_sets_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'component_sets'
    component_sets = common_processor(base_path, 'component_sets', item_category, i18n_zhcn_map, i18n_en_map, version,
                                      icons, all_global_var)
    component_sets_data = component_sets_refinery(component_sets, icons)
    save_data(item_category, component_sets_data)
    return component_sets_data


# component_templates 组件模板
def component_templates_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var,
                                  component_sets):
    item_category = 'component_templates'
    pp = ParadoxParser(os.path.join(base_path + 'common\\component_templates\\weapon_components.csv'), item_category)
    component_add = pp.data
    component_templates = common_processor(base_path, 'component_templates', item_category, i18n_zhcn_map, i18n_en_map,
                                           version, icons, all_global_var)
    component_templates_data = component_templates_refinery(component_templates, i18n_zhcn_map, i18n_en_map, icons,
                                                            component_sets, component_add)
    save_data(item_category, component_templates_data)
    return component_templates_data


# ship_behaviors 舰船行为
def ship_behaviors_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'ship_behaviors'
    ship_behaviors = common_processor(base_path, 'ship_behaviors', item_category, i18n_zhcn_map, i18n_en_map,
                                      version, icons, all_global_var)
    ship_behaviors_data = ship_behaviors_refinery(ship_behaviors, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, ship_behaviors_data)
    return ship_behaviors_data


# ship_sizes 舰船类型
def ship_sizes_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'ship_sizes'
    ship_sizes = common_processor(base_path, 'ship_sizes', item_category, i18n_zhcn_map, i18n_en_map,
                                  version, icons, all_global_var)
    ship_sizes_data = ship_sizes_refinery(ship_sizes, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, ship_sizes_data)
    return ship_sizes_data


# starbase_buildings 恒星基地建筑
def starbase_buildings_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'starbase_buildings'
    starbase_buildings = common_processor(base_path, 'starbase_buildings', item_category, i18n_zhcn_map, i18n_en_map,
                                          version, icons, all_global_var)
    starbase_buildings_data = starbase_buildings_refinery(starbase_buildings, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, starbase_buildings_data)
    return starbase_buildings_data


# starbase_levels_data 恒星基地等级
def starbase_levels_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'starbase_levels'
    starbase_levels = common_processor(base_path, 'starbase_levels', item_category, i18n_zhcn_map, i18n_en_map, version,
                                       icons, all_global_var)
    starbase_levels_data = starbase_levels_refinery(starbase_levels, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, starbase_levels_data)
    return starbase_levels_data


# starbase_modules 恒星基地模块
def starbase_modules_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'starbase_modules'
    starbase_modules = common_processor(base_path, 'starbase_modules', item_category, i18n_zhcn_map, i18n_en_map,
                                        version, icons, all_global_var)
    starbase_modules_data = starbase_modules_refinery(starbase_modules, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, starbase_modules_data)
    return starbase_modules_data


# Agendas 议程
def agendas_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'agendas'
    agendas = common_processor(base_path, 'agendas', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                               all_global_var)
    agenda_data = agendas_refinery(agendas, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, agenda_data)
    return agenda_data


# Subjects 附庸
def subjects_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'subjects'
    subjects = common_processor(base_path, 'subjects', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                all_global_var)
    subjects_data = subjects_refinery(subjects, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, subjects_data)
    return subjects_data


# Bombardment_stances 轨道轰炸姿态
def bombardment_stances_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'bombardment_stances'
    bombardment_stances = common_processor(base_path, 'bombardment_stances', item_category, i18n_zhcn_map, i18n_en_map,
                                           version, icons, all_global_var)
    bombardment_stances_data = bombardment_stances_refinery(bombardment_stances, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, bombardment_stances_data)
    return bombardment_stances_data


# personalities AI性格
def personalities_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'personalities'
    personalities = common_processor(base_path, 'personalities', item_category, i18n_zhcn_map, i18n_en_map, version,
                                     icons, all_global_var)
    personalities_data = personalities_refinery(personalities, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, personalities_data)
    return personalities_data


# Pop_faction_types派系
def pop_faction_types_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'pop_faction_types'
    pft = common_processor(base_path, 'pop_faction_types', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                           all_global_var)
    pft_data = pft_refinery(pft, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, pft_data)
    return pft_data


# Casus_belli宣战借口
def casus_belli_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, war_goals):
    item_category = 'casus_belli'
    casus_belli = common_processor(base_path, 'casus_belli', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                   all_global_var)
    casus_belli_data = casus_belli_refinery(casus_belli, i18n_zhcn_map, i18n_en_map, war_goals)
    save_data(item_category, casus_belli_data)
    return casus_belli_data


# War_goals战争目标
def war_goals_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'war_goals'
    war_goals = common_processor(base_path, 'war_goals', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                 all_global_var)
    war_goals_data = war_goals_refinery(war_goals, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, war_goals_data)
    return war_goals_data


# Policies政策
def policies_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'policies'
    policies = common_processor(base_path, 'policies', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                all_global_var)
    policies_data = policies_refinery(policies, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, policies_data)
    return policies_data


# Armies陆军
def armies_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'armies'
    armies = common_processor(base_path, 'armies', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                              all_global_var)
    armies_data = armies_refinery(armies)
    save_data(item_category, armies_data)
    return armies_data


# Authorities 权利制度
def authorities_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'authorities'
    authorities = common_processor(base_path, 'governments\\authorities', item_category, i18n_zhcn_map, i18n_en_map,
                                   version, icons, all_global_var)
    authorities_data = authorities_refinery(authorities, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, authorities_data)
    return authorities_data


# Ethics 思潮
def ethics_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'ethics'
    ethics = common_processor(base_path, 'ethics', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                              all_global_var)
    ethic_data = ethics_refinery(ethics)
    save_data(item_category, ethic_data)
    return ethic_data


# Traits 特性
def traits_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'traits'
    traits = common_processor(base_path, 'traits', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                              all_global_var)
    traits_data = traits_refinery(traits, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, traits_data)
    return traits_data


# Planet_classes 行星类型
def planet_classes_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'planet_classes'
    planet_classes = common_processor(base_path, 'planet_classes', item_category, i18n_zhcn_map, i18n_en_map, version,
                                      icons, all_global_var)
    planet_classes_data = planet_classes_refinery(planet_classes, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, planet_classes_data)
    return planet_classes_data


# Star_classes 行星类型
def star_classes_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, planet_classes):
    item_category = 'star_classes'
    star_classes = common_processor(base_path, 'star_classes', item_category, i18n_zhcn_map, i18n_en_map, version,
                                    icons, all_global_var)
    star_classes_data = star_classes_data_refinery(star_classes, i18n_zhcn_map, i18n_en_map, planet_classes)
    save_data(item_category, star_classes_data)
    return star_classes_data


# Terraform 地貌改造
def terraform_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, planet_classes):
    item_category = 'terraform'
    terraform = common_processor(base_path, 'terraform', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                 all_global_var)
    terraform_data = terraform_refinery(terraform, i18n_zhcn_map, i18n_en_map, planet_classes)
    save_data(item_category, terraform_data)
    return terraform_data


# Static_modifiers 修正
def static_modifiers_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'static_modifiers'
    static_modifiers = common_processor(base_path, 'static_modifiers', item_category, i18n_zhcn_map, i18n_en_map,
                                        version, icons, all_global_var)
    static_modifiers_data = static_modifiers_refinery(static_modifiers, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, static_modifiers_data)
    return static_modifiers_data


# Planet_modifiers 行星修正
def planet_modifiers_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, static_modifiers):
    item_category = 'planet_modifiers'
    planet_modifiers = common_processor(base_path, 'planet_modifiers', item_category, i18n_zhcn_map, i18n_en_map,
                                        version, icons, all_global_var)
    planet_modifiers_data = planet_modifiers_refinery(planet_modifiers, i18n_zhcn_map, i18n_en_map, static_modifiers)
    save_data(item_category, planet_modifiers_data)
    return planet_modifiers_data


# Civics 国家理念
def civics_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'civics'
    civics = common_processor(base_path, 'governments\\civics', item_category, i18n_zhcn_map, i18n_en_map, version,
                              icons, all_global_var)
    civics_data = civics_refinery(civics, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, civics_data)
    return civics_data


# Governments 政府
def governments_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'governments'
    governments = common_processor(base_path, 'governments', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                   all_global_var)
    governments_data = governments_refinery(governments, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, governments_data)
    return governments_data


# Edicts 法令
def edicts_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'edicts'
    edicts = common_processor(base_path, 'edicts', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                              all_global_var)
    edicts_data = edicts_refinery(edicts, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, edicts_data)
    return edicts_data


# Tradition category 传统分类
def tradition_cats_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'tradition_categories'
    tradition_cats = common_processor(base_path, 'tradition_categories', item_category, i18n_zhcn_map, i18n_en_map,
                                      version, icons, all_global_var)
    return tradition_cats_refinery(tradition_cats)


# Traditions 传统
def traditions_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, tradition_cats):
    item_category = 'traditions'
    traditions = common_processor(base_path, 'traditions', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                  all_global_var)
    traditions_data = traditions_refinery(traditions, i18n_zhcn_map, i18n_en_map, tradition_cats)
    save_data(item_category, traditions_data)
    return traditions_data


# ascension_perks 飞升天赋
def ascension_perks_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'ascension_perks'
    ascension_perks = common_processor(base_path, 'ascension_perks', item_category, i18n_zhcn_map, i18n_en_map, version,
                                       icons, all_global_var)
    ascension_perks_data = ascension_perks_refinery(ascension_perks, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, ascension_perks_data)
    return ascension_perks_data


# Tile_blockers 地块障碍
def tile_blockers_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'tile_blockers'
    tile_blockers = common_processor(base_path, 'tile_blockers', item_category, i18n_zhcn_map, i18n_en_map, version,
                                     icons, all_global_var)
    tile_blockers_data = tile_blockers_refinery(tile_blockers)
    save_data(item_category, tile_blockers_data)
    return tile_blockers_data


# strategic_resources战略资源
def strategic_resources_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'strategic_resources'
    strategic_resources = common_processor(base_path, 'strategic_resources', item_category, i18n_zhcn_map, i18n_en_map,
                                           version, icons, all_global_var)
    strategic_resources_data = strategic_resources_refinery(strategic_resources, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, strategic_resources_data)
    return strategic_resources_data


# deposits资源点
def deposits_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var, planet_modifiers):
    item_category = 'deposits'
    deposits = common_processor(base_path, 'deposits', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                all_global_var)
    deposits_data = deposits_refinery(deposits, i18n_zhcn_map, i18n_en_map, planet_modifiers)
    save_data(item_category, deposits_data)
    return deposits_data


# buildings建筑
def buildings_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'buildings'
    buildings = common_processor(base_path, 'buildings', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                 all_global_var)
    buildings_data = buildings_refinery(buildings, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, buildings_data)
    return buildings_data


# technology科技
def technology_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'technology'
    technology = common_processor(base_path, 'technology', item_category, i18n_zhcn_map, i18n_en_map, version, icons,
                                  all_global_var)
    technology_data = technology_refinery(technology, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, technology_data)
    return technology_data


# achievements成就
def achievements_processor(base_path, i18n_zhcn_map, i18n_en_map, version, icons, all_global_var):
    item_category = 'achievements'
    achievements = text_processor(base_path, 'achievements.txt', item_category)
    achievements_data = achievements_refinery(achievements, i18n_zhcn_map, i18n_en_map)
    save_data(item_category, achievements_data)
    return achievements_data


# 添加一些重要字段，方便查询
def add_important_keys(raw_dict, item_category, i18n_zhcn_map, i18n_en_map, version, icons):
    for key, info in raw_dict.items():
        temp_info = OrderedDict()
        temp_info['key'] = key
        temp_info['main_category'] = item_category
        temp_info['version'] = version

        # zhcn_name, en_name 名称
        if item_category != 'deposits':
            temp_info['zhcn_name'], temp_info['en_name'] = zhcn(key, i18n_zhcn_map, i18n_en_map)
        else:
            if 'resources' in info:
                temp_str = ''
                for res_name in info['resources']:
                    temp_str += '£'
                    if res_name in pdx_resource:
                        temp_str += pdx_resource[res_name] + ' '
                    else:
                        temp_str += res_name + ' '
                    if res_name != 'sr_alien_pets' and res_name != 'sr_betharian':
                        temp_str += info['resources'][res_name] + ' '
                Danteng.log(temp_str)
                temp_info['zhcn_name'] = temp_str
                temp_info['en_name'] = temp_str
                i18n_zhcn_map[key] = temp_str
                i18n_en_map[key] = temp_str
            else:
                temp_info['zhcn_name'] = '空地'
                temp_info['en_name'] = 'null'
                i18n_zhcn_map[key] = '空地'
                i18n_en_map[key] = 'null'

        # zhcn_desc, en_desc 描述
        temp_info['zhcn_desc'], temp_info['en_desc'] = zhcn(key + '_desc', i18n_zhcn_map, i18n_en_map, True)

        instruction = ''
        if 'tags' in info:
            for i in info['tags']:
                instruction = zhcn(i, i18n_zhcn_map, i18n_en_map)[0] + '\\n'
            temp_info['instruction'] = instruction[0:-2]
            Danteng.log(temp_info['zhcn_name'] + '\\n' + temp_info['instruction'])

        # 修正
        modifiers = ['modifier', 'planet_modifier', 'country_modifier', 'system_modifier', 'station_modifier',
                     'ship_modifier', 'orbit_modifier', 'army_modifier', 'self_modifier', 'adjacency_bonus']
        logics = ['random_weight', 'weight_modifier', 'potential', 'orbital_weight', 'drop_weight', 'ai_weight',
                  'spawn_chance', 'allow', 'ai_allow', 'show_tech_unlock_if', 'destroy_if', 'active', 'weight',
                  'election_candidates', 'condition']
        # 还有triggered_planet_modifier和planet_modifier_with_pop_trigger，蠢驴暂时未启用
        # 保留原名称对应的原始数据，同时展示出具体效果
        # 以防翻译内容更新，重新从翻译中读取
        for modifier_name in modifiers:
            if modifier_name in info:
                if len(info[modifier_name]) == 0:
                    info.pop(modifier_name)
                else:
                    Danteng.log('\n' + temp_info['zhcn_name'] + '的modifier：' + modifier_name)
                    name = 'zhcn_' + modifier_name
                    temp_info[name] = modifier_processor(info[modifier_name], i18n_zhcn_map, i18n_en_map)

        for logic_name in logics:
            if logic_name in info:
                if len(info[logic_name]) == 0:
                    info.pop(logic_name)
                else:
                    Danteng.log('\n' + temp_info['zhcn_name'] + '的logic：' + logic_name)
                    if logic_name in pdx_logic:
                        logic_zhcn_name = pdx_logic[logic_name]['value']
                    else:
                        logic_zhcn_name = zhcn(logic_name, i18n_zhcn_map, i18n_en_map)[0]
                    logic_it(logic_name, info, i18n_zhcn_map, i18n_en_map, logic_zhcn_name, raw_dict,
                             temp_info['zhcn_name'])
        temp_info.update(info)

        # possible
        if 'possible' in info:
            Danteng.log('\n' + temp_info['zhcn_name'] + '的possible：')
            name = 'possible_desc'
            temp_info[name] = i18n_zhcn_map['REQUIREMENTS'] + '\\n' + possible_processor(info['possible'],
                                                                                         i18n_zhcn_map, i18n_en_map)
            temp_info[name] = modifier_replace(temp_info[name])
            Danteng.log(temp_info[name])

        if temp_info['main_category'] == 'pop_faction_types':
            temp_info['icon'] = icons['GFX_faction_icon_' + temp_info['key']]['icon']
        if 'icon' in info:
            temp_info['icon'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', info['icon'].replace('"', ''))
            if temp_info['icon'] in icons:
                temp_info['icon'] = icons[temp_info['icon']]['icon']
        # 前置科技
        if 'prerequisites' in temp_info:
            if len(temp_info['prerequisites']) == 0:
                temp_info.pop('prerequisites')
            else:
                find = re.findall(r'\"(.*?)\"', temp_info['prerequisites'][0])
                if find:
                    temp_info['prerequisites'] = find
        # 最后更新数据
        raw_dict[key] = temp_info


def icons_refinery(data):
    data = data['spriteTypes']['spriteType']
    temp_data = {}
    for i in range(len(data)):
        temp_data[data[i]['name'].replace('"', '')] = data[i]
    data = temp_data
    for icon_name, icon_value in data.items():
        if 'name' in icon_value:
            icon_value['key'] = icon_value['name'].replace('"', '')
            icon_value.pop('name')
        if 'texturefile' in icon_value:
            icon_value['textureFile'] = icon_value['texturefile']
            icon_value.pop('texturefile')
        if 'textureFile' in icon_value:
            icon_value['textureFile'] = icon_value['textureFile'].replace('"', '')
            icon_value['icon'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', icon_value['textureFile'])
    return data


def ethics_refinery(data):
    refined_data = OrderedDict()
    for ethic_name, ethics_value in data.items():
        if ethic_name != 'ethic_categories':
            refined_data[ethic_name] = ethics_value
    return refined_data


def authorities_refinery(data, i18n_zhcn_map, i18n_en_map):
    for name, value in data.items():
        value['desc_detail'] = ''
        value['desc_detail'] = authorities_detail_processor(value, i18n_zhcn_map, i18n_en_map)
    return data


def planet_classes_refinery(data, i18n_zhcn_map, i18n_en_map):
    refined_data = OrderedDict()
    for pc_name, pc_value in data.items():
        if pc_name[0:3] == 'pc_':
            if 'climate' in pc_value:
                climate = pc_value['climate'][1:-1]
                pc_value['climate_desc'] = zhcn(climate, i18n_zhcn_map, i18n_en_map)[0]
            pc_value['desc_detail'] = '模型大小：' + pc_value['entity_scale'] + '\\n' + '星球大小：'
            if 'max' in pc_value['planet_size'] and 'min' in pc_value['planet_size']:
                pc_value['desc_detail'] += pc_value['planet_size']['min'] + '~' + pc_value['planet_size']['max'] + '\\n'
            else:
                pc_value['desc_detail'] += pc_value['planet_size'] + '\\n'
            if 'moon_size' in pc_value:
                if 'max' in pc_value['moon_size'] and 'min' in pc_value['moon_size']:
                    pc_value['desc_detail'] += '卫星大小：' + pc_value['moon_size']['min'] + '~' + \
                                               pc_value['moon_size']['max'] + '\\n'
                else:
                    pc_value['desc_detail'] += '卫星大小：' + pc_value['moon_size'] + '\\n'
            if 'spawn_odds' in pc_value:
                pc_value['desc_detail'] += '出现概率：' + pc_value['spawn_odds'] + '\\n'
            if not ('star' in pc_value) or pc_value['star'] != 'yes':
                if 'min_distance_from_sun' in pc_value and 'max_distance_from_sun' in pc_value:
                    pc_value['desc_detail'] += '到恒星距离：' + pc_value['min_distance_from_sun'] + '~' + \
                                               pc_value['max_distance_from_sun']
            if pc_name[0:12] == 'pc_ringworld':
                pc_value['desc_detail'] += '到恒星距离：' + '45'
            refined_data[pc_name] = pc_value
            if 'icon_frame' in pc_value:
                pc_value['icon'] = 'planet_type_' + pc_value['icon_frame']
            if not ('star' in pc_value):
                pc_value['star'] = 'no'
            if 'picture' in pc_value:
                pc_value['picture'] = pc_value['picture'].replace('"', '')
        if 'zhcn_desc' in pc_value and pc_value['zhcn_desc'] == '[Root.GetGrayGooWorldDesc]':
            pc_value['zhcn_desc'] = '§H无全局变量§Yactive_gray_goo§!时描述：§!\\n' + \
                                    zhcn('gray_goo_world_inactive_nanites', i18n_zhcn_map, i18n_en_map)[0] + \
                                    '\\n§H拥有全局变量§Yactive_gray_goo§!时的描述：§!\\n' + \
                                    zhcn('gray_goo_world_active_nanites', i18n_zhcn_map, i18n_en_map)[0]
    return refined_data


def static_modifiers_refinery(data, i18n_zhcn_map, i18n_en_map):
    non_include = ['modifier', 'icon_frame', 'icon', 'key', 'main_category', 'zhcn_name', 'zhcn_desc', 'en_name',
                   'en_desc', 'version']
    refined_data = OrderedDict()
    for sm_name, sm_value in data.items():
        sm_value['modifier'] = OrderedDict()
        for key in sm_value:
            if not (key in non_include):
                sm_value['modifier'][key] = sm_value[key]
        refined_data[sm_name] = OrderedDict()
        for key in non_include:
            if key in sm_value:
                refined_data[sm_name][key] = data[sm_name][key]
    for sm_name, sm_value in refined_data.items():
        sm_value['zhcn_modifier'] = modifier_processor(sm_value['modifier'], i18n_zhcn_map, i18n_en_map)
    return refined_data


def planet_modifiers_refinery(data, i18n_zhcn_map, i18n_en_map, static_modifiers):
    for pc_name, pc_value in data.items():
        if 'zhcn_modifier' in pc_value:
            pc_value['zhcn_name'] = pc_value['zhcn_modifier']
        if 'modifier' in pc_value:
            pc_value['modifier'] = pc_value['modifier'].replace('"', '')
            if pc_value['modifier'] in static_modifiers:
                pc_value['en_name'] = static_modifiers[pc_value['modifier']]['en_name']
                pc_value['zhcn_modifier'] = static_modifiers[pc_value['modifier']]['zhcn_modifier']
                pc_value['zhcn_desc'] = static_modifiers[pc_value['modifier']]['zhcn_desc']
                pc_value['en_desc'] = static_modifiers[pc_value['modifier']]['en_desc']
                if static_modifiers[pc_value['modifier']]['icon']:
                    pc_value['icon'] = static_modifiers[pc_value['modifier']]['icon']
                    pc_value['icon_frame'] = static_modifiers[pc_value['modifier']]['icon_frame']
        else:
            pc_value['en_name'] = ''
            pc_value['zhcn_modifier'] = ''
            pc_value['zhcn_desc'] = ''
            pc_value['en_desc'] = ''
            pc_value['icon'] = 'modifier_background'
    for pc_name, pc_value in data.items():
        if 'spawn_chance' in pc_value and len(pc_value['spawn_chance']) != 0:
            logic_it('spawn_chance', pc_value, i18n_zhcn_map, i18n_en_map, '出现概率', data)
        else:
            pc_value['spawn_chance_logic'] = pdx_logic['spawn_chance']['value'] + '\\n※14无'
    return data


def civics_refinery(data, i18n_zhcn_map, i18n_en_map):
    for civic_name, civic_value in data.items():
        if 'description' in civic_value:
            desc = civic_value['description'].replace('"', '')
            civic_value['zhcn_modifier'] = zhcn(desc, i18n_zhcn_map, i18n_en_map)[0]
            find = re.findall(r'\$.*?\$', civic_value['zhcn_modifier'])
            if find:
                for item in find:
                    find_key = item[1:-1]
                    if find_key in i18n_zhcn_map:
                        civic_value['zhcn_modifier'] = civic_value['zhcn_modifier'].replace(item,
                                                                                            i18n_zhcn_map[find_key])
                        Danteng.log(civic_name)
                        civic_value['en_modifier'] = civic_value['en_modifier'].replace(item, i18n_en_map[find_key])
                    elif find_key in i18n_en_map:
                        civic_value['zhcn_modifier'] = civic_value['zhcn_modifier'].replace(item, i18n_en_map[find_key])
                        civic_value['en_modifier'] = civic_value['en_modifier'].replace(item, i18n_en_map[find_key])
        if 'zhcn_modifier' in civic_value:
            Danteng.log(civic_value['zhcn_modifier'])
        if 'random_weight_logic' in civic_value:
            if civic_value['random_weight_logic'].find('game_started') != -1:
                civic_value['moddable'] = 'false'
            else:
                civic_value['moddable'] = 'true'
        if 'playable' in civic_value:
            civic_value['potential_logic'] += "\\n※14▲拥有§H" + pdx_logic[
                civic_value['playable']['host_has_dlc'].replace('"', '')]['value'] + "§!DLC"
        # if 'potential_logic' in civic_value:
        #     if civic_value['potential_logic'].find('国家类型是§H') != -1:
        #         civic_value['icon'] = 'civic_agrarian_idyll'
    return data


def strategic_resources_refinery(data, i18n_zhcn_map, i18n_en_map):
    for sr_name, sr_value in data.items():
        if 'AI_category' in sr_value:
            sr_value['zhcn_AI_category'], sr_value['en_AI_category'] = zhcn(sr_value['AI_category'], i18n_zhcn_map,
                                                                            i18n_en_map)
            Danteng.log(sr_value['zhcn_AI_category'])
        if sr_value['zhcn_name'] == 'time':
            sr_value['zhcn_name'] = '时间'
        if 'base_income' in sr_value and type(sr_value['base_income']) == list:
            sr_value['base_income'] = sr_value['base_income'][len(sr_value['base_income']) - 1]
    return data


def deposits_refinery(data, i18n_zhcn_map, i18n_en_map, planet_modifiers):
    for deposit_name, deposit_value in data.items():
        Danteng.log(deposit_value['zhcn_name'])
        if 'station' in deposit_value:
            deposit_value['zhcn_station'], deposit_value['en_station'] = zhcn('station', i18n_zhcn_map, i18n_en_map)
        if 'drop_weight_logic' in deposit_value:
            temp = deposit_value['drop_weight_logic']
            find = re.findall(r'(pm_.*?)\\n', temp)
            if find:
                for item in find:
                    find_key = item
                    if find_key in planet_modifiers:
                        temp = temp.replace(item, '§H' + planet_modifiers[find_key]['zhcn_name'] + '§!')
            deposit_value['drop_weight_logic'] = temp
    return data


def buildings_refinery(data, i18n_zhcn_map, i18n_en_map):
    for building_name, building_value in data.items():
        icon_dict = {'produced_resources', 'cost', 'required_resources'}
        Danteng.log(building_name)
        for item in icon_dict:
            if item in building_value:
                temp_str = ''
                for res in building_value[item]:
                    if res in pdx_resource:
                        res_icon = '£' + pdx_resource[res]
                    else:
                        res_icon = '£' + res
                    temp_str += res_icon + ' ' + building_value[item][res] + ' '
                building_value[item + '_string'] = temp_str
        if 'produced_resource_trigger' in building_value:
            logic_it('produced_resource_trigger', building_value, i18n_zhcn_map, i18n_en_map, '额外产出修正', data)
            for icon_item in pdx_resource:
                building_value['produced_resource_trigger_logic'] = \
                    re.sub(icon_item + r':\s*(\d*)', '£' + pdx_resource[icon_item] + r'\1',
                           building_value['produced_resource_trigger_logic'])
        if 'adjacency_bonus' in building_value:
            bonus_str = ''
            for bonus_item in building_value['adjacency_bonus']:
                bonus_str += zhcn(bonus_item, i18n_zhcn_map, i18n_en_map)[0] + ':§G+' + \
                             building_value['adjacency_bonus'][bonus_item] + '§!\\n'
            building_value['adjacency_bonus_string'] = bonus_str
            Danteng.log(building_value['adjacency_bonus_string'])
    return data


def technology_refinery(data, i18n_zhcn_map, i18n_en_map):
    tech_icon = {}
    for tech_name, tech_value in data.items():
        if 'zhcn_modifier' not in tech_value:
            tech_value['zhcn_modifier'] = ''
        if 'icon' in tech_value:
            if tech_value['icon'] == 't_space_construction':
                tech_value.pop('icon')
        if 'category' in tech_value:
            if type(tech_value['category']) != str:
                tech_value['category'] = tech_value['category'][0]
            tech_value['zhcn_category'] = i18n_zhcn_map[tech_value['category']]
        if 'feature_flags' in tech_value:
            temp_feature = ''
            for i in range(len(tech_value['feature_flags'])):
                temp_feature += '§H解锁特性：§!' + zhcn('feature_' + tech_value['feature_flags'][i], i18n_zhcn_map,
                                                   i18n_en_map)[0] + '\\n'

            if 'zhcn_modifier' in tech_value:
                if tech_value['zhcn_modifier'][-2:] == '\\n':
                    tech_value['zhcn_modifier'] += temp_feature
                else:
                    tech_value['zhcn_modifier'] += '\\n' + temp_feature
            else:
                tech_value['zhcn_modifier'] = temp_feature
        if 'prereqfor_desc' in tech_value:
            Danteng.log(tech_name)
            if 'zhcn_modifier' in tech_value:
                temp = tech_value['zhcn_modifier']
            else:
                temp = '\\n'
            if temp[-2:] != '\\n':
                temp += '\\n'
            for item in tech_value['prereqfor_desc']:
                if item != 'hide_prereq_for_desc':
                    if type(tech_value['prereqfor_desc'][item]) == list:
                        for i in range(len(tech_value['prereqfor_desc'][item])):
                            string = tech_value['prereqfor_desc'][item][i]['title'].replace('"', '')
                            tech_value['zhcn_modifier'] = temp + zhcn(string, i18n_zhcn_map, i18n_en_map)[0]
                    else:
                        string = tech_value['prereqfor_desc'][item]['title'].replace('"', '')
                        tech_value['zhcn_modifier'] = temp + zhcn(string, i18n_zhcn_map, i18n_en_map)[0]
            Danteng.log(tech_value['zhcn_modifier'])
        if tech_value['zhcn_modifier'][0:2] == '\\n':
            tech_value['zhcn_modifier'] = tech_value['zhcn_modifier'][2:]
        if 'is_dangerous' in tech_value and type(tech_value['is_dangerous']) != str:
            tech_value['is_dangerous'] = tech_value['is_dangerous'][len(tech_value['is_dangerous']) - 1]
        tech_url = 'https://cdn.huijiwiki.com/qunxing/index.php?title=special:redirect/file/' + tech_value['key'] \
                   + '.png'
        tech_icon[tech_value['key']] = requests.get(tech_url).url
    tech_json = json.dumps(tech_icon, ensure_ascii=False)
    with open('json\\tech_icon.json', 'w', encoding='UTF-8') as f:
        f.write(tech_json)
    return data


def governments_refinery(data, i18n_zhcn_map, i18n_en_map):
    title = ['ruler_title', 'ruler_title_female', 'heir_title', 'heir_title_female', 'leader_class']
    for gov_name, gov_value in data.items():
        for item in title:
            if item in gov_value:
                gov_value[item + '_desc'] = zhcn(gov_value[item], i18n_zhcn_map, i18n_en_map)[0]
                Danteng.log(gov_value[item + '_desc'])
    return data


def traditions_refinery(data, i18n_zhcn_map, i18n_en_map, tradition_cats):
    for tr_name, tr_value in data.items():
        tr_value['icon'] = re.sub(r'^tr_', r'tradition_', tr_value['key'])
        if 'tradition_swap' in tr_value:
            if type(tr_value['tradition_swap']) != list:
                temp = [tr_value['tradition_swap']]
                tr_value['tradition_swap'] = temp
            for i in range(len(tr_value['tradition_swap'])):
                tr_swap_name = tr_value['tradition_swap'][i]['name']
                tr_value['tradition_swap'][i]['zhcn_name'], tr_value['tradition_swap'][i]['en_name'] = zhcn(
                    tr_swap_name, i18n_zhcn_map, i18n_en_map)
                tr_value['tradition_swap'][i]['zhcn_desc'], tr_value['tradition_swap'][i]['en_desc'] = zhcn(
                    tr_swap_name + '_desc', i18n_zhcn_map, i18n_en_map, True)
                tr_value['tradition_swap'][i]['icon'] = re.sub(r'^tr_', r'tradition_', tr_value['tradition_swap'][i][
                    'name'])
                if '_finish' in tr_value['key'] or '_adopt' in tr_value['key']:
                    Danteng.log('传统的key：' + tr_value['key'])
                    tr_value['tradition_swap'][i]['icon'] = 'Menu_icon_traditions'
                if 'trigger' in tr_value['tradition_swap'][i]:
                    logic_it('trigger', tr_value['tradition_swap'][i], i18n_zhcn_map, i18n_en_map, '触发条件', data)
                if 'modifier' in tr_value['tradition_swap'][i]:
                    Danteng.log('\n' + tr_value['tradition_swap'][i]['zhcn_name'] + '的modifier：' + 'modifier')
                    tr_value['tradition_swap'][i]['zhcn_modifier'] = modifier_processor(
                        tr_value['tradition_swap'][i]['modifier'], i18n_zhcn_map, i18n_en_map)
                if 'weight' in tr_value['tradition_swap'][i]:
                    logic_it('weight', tr_value['tradition_swap'][i], i18n_zhcn_map, i18n_en_map, '基础权重', data)
        if '_finish' in tr_value['key'] or '_adopt' in tr_value['key']:
            tr_value['icon'] = 'Menu_icon_traditions'
        if tr_name in tradition_cats:
            tr_value['category'] = tradition_cats[tr_name]
    return data


def tile_blockers_refinery(data):
    for tb_name, tb_value in data.items():
        if tb_value['zhcn_name'][0:3] == 'tb_':
            tb_value['zhcn_name'] += ' (未知地块障碍)'
        elif tb_value['zhcn_name'][0:9] == '£blocker ':
            tb_value['zhcn_name'] = tb_value['zhcn_name'][9:]
            tb_value['en_name'] = tb_value['en_name'][9:]
        if 'picture' in tb_value:
            tb_value['icon'] = tb_value['picture'] + '_01'
        else:
            tb_value['icon'] = tb_value['key'] + '_01'
        if ('cost' in tb_value and len(tb_value['cost']) > 0) or ('time' in tb_value):
            tb_value['zhcn_cost'] = '§E花费：'
            if 'cost' in tb_value and len(tb_value['cost']) > 0:
                for item in tb_value['cost']:
                    if item in pdx_resource:
                        tb_value['zhcn_cost'] += '£' + pdx_resource[item] + tb_value['cost'][item]
            if 'time' in tb_value:
                tb_value['zhcn_cost'] += '£time' + tb_value['time']
            tb_value['zhcn_cost'] += '§!'
    return data


def ascension_perks_refinery(data, i18n_zhcn_map, i18n_en_map):
    for ap_name, ap_value in data.items():
        if 'on_enabled' in ap_value:
            if 'custom_tooltip' in ap_value['on_enabled']:
                if type(ap_value['on_enabled']['custom_tooltip']) == str:
                    temp_str = ap_value['on_enabled']['custom_tooltip']
                    ap_value['on_enabled']['custom_tooltip'] = [temp_str]
                for i in range(len(ap_value['on_enabled']['custom_tooltip'])):
                    if 'custom_tooltip' in ap_value['on_enabled']:
                        tooltip = ap_value['on_enabled']['custom_tooltip'][i].replace('"', '')
                        temp = zhcn(tooltip, i18n_zhcn_map, i18n_en_map)[0]
                        if 'zhcn_modifier' in ap_value:
                            if ap_value['zhcn_modifier'][-2:] == '\\n':
                                ap_value['zhcn_modifier'] = ap_value['zhcn_modifier'][0:-2]
                            ap_value['zhcn_modifier'] += '\\n' + temp
                        else:
                            ap_value['zhcn_modifier'] = temp
    return data


def terraform_refinery(data, i18n_zhcn_map, i18n_en_map, planet_classes):
    for terraform_name, terraform_value in data.items():
        if ('from' in terraform_value) and ('to' in terraform_value):
            terraform_value['from_icon'] = planet_classes[terraform_value['from']]['icon']
            terraform_value['to_icon'] = planet_classes[terraform_value['to']]['icon']
            tf, tf_en = zhcn(terraform_value['from'], i18n_zhcn_map, i18n_en_map)
            tt, tt_en = zhcn(terraform_value['to'], i18n_zhcn_map, i18n_en_map)
            terraform_value['zhcn_name'] = tf + '→' + tt
            terraform_value['en_name'] = tf_en + ' to ' + tt_en
    return data


def traits_refinery(data, i18n_zhcn_map, i18n_en_map):
    for traits_name, traits_value in data.items():
        if 'allowed_archetypes' in traits_value:
            find = re.findall(r'(\S+)', traits_value['allowed_archetypes'][0])
            if find:
                traits_value['allowed_archetypes'] = find
            traits_value['zhcn_archetypes'] = list.copy(traits_value['allowed_archetypes'])
            for i in range(len(traits_value['zhcn_archetypes'])):
                traits_value['zhcn_archetypes'][i] = zhcn(traits_value['zhcn_archetypes'][i],
                                                          i18n_zhcn_map, i18n_en_map)[0]
        if 'custom_tooltip' in traits_value:
            traits_value['zhcn_modifier'] = zhcn(traits_value['custom_tooltip'], i18n_zhcn_map, i18n_en_map)[0]
        elif 'zhcn_self_modifier' in traits_value:
            traits_value['zhcn_modifier'] = traits_value['zhcn_self_modifier']
        if 'ai_categories' in traits_value:
            for i in range(len(traits_value['ai_categories'])):
                traits_value['ai_categories'][i] = zhcn(traits_value['ai_categories'][i], i18n_zhcn_map, i18n_en_map)[0]
        if 'leader_potential_add' in traits_value:
            logic_it('leader_potential_add', traits_value, i18n_zhcn_map, i18n_en_map, '可能性加成', data)
        if 'species_potential_add' in traits_value:
            logic_it('species_potential_add', traits_value, i18n_zhcn_map, i18n_en_map, '可能性加成', data)
        if 'opposites' in traits_value:
            find = re.findall(r'\"(.*?)\"', traits_value['opposites'][0])
            if find:
                traits_value['opposites'] = find
        if 'leader_class' in traits_value:
            find = re.findall(r'(\S+)', traits_value['leader_class'][0])
            if find:
                traits_value['leader_class'] = find
            traits_value['zhcn_leader_class'] = list.copy(traits_value['leader_class'])
            for i in range(len(traits_value['leader_class'])):
                traits_value['zhcn_leader_class'][i] = zhcn(traits_value['leader_class'][i],
                                                            i18n_zhcn_map, i18n_en_map)[0]
    return data


def edicts_refinery(data, i18n_zhcn_map, i18n_en_map):
    for edicts_name, edicts_value in data.items():
        if 'cost' in edicts_value and len(edicts_value['cost']) > 0:
            edicts_value['zhcn_cost'] = '§E基础花费：§!'
            for item in edicts_value['cost']:
                if item in pdx_resource:
                    edicts_value['zhcn_cost'] += '£' + pdx_resource[item] + edicts_value['cost'][item]
        if 'effect' in edicts_value and len(edicts_value['effect']) > 0:
            if 'custom_tooltip' in edicts_value['effect']:
                edicts_value['zhcn_modifier'] = zhcn(edicts_value['effect']['custom_tooltip'],
                                                     i18n_zhcn_map, i18n_en_map)[0]
            elif 'if' in edicts_value['effect']:
                edicts_value['zhcn_modifier'] = choice(edicts_value['effect'], i18n_zhcn_map, i18n_en_map, 1)[2:]
    return data


def megastructures_refinery(data, i18n_zhcn_map, i18n_en_map):
    for ms_name, ms_value in data.items():
        if 'portrait' in ms_value:
            ms_value['portrait'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', ms_value['portrait']).replace('"', '')
        if 'build_cost' in ms_value and len(ms_value['build_cost']) > 0:
            ms_value['zhcn_cost'] = '§E成本：§!'
            for item in ms_value['build_cost']:
                if item in pdx_resource:
                    ms_value['zhcn_cost'] += '£' + pdx_resource[item] + ms_value['build_cost'][item]
        if 'maintenance' in ms_value and len(ms_value['maintenance']) > 0:
            ms_value['zhcn_maintenance'] = '§E维护费用：§!'
            for item in ms_value['maintenance']:
                if item in pdx_resource:
                    ms_value['zhcn_maintenance'] += '£' + pdx_resource[item] + \
                                                    ms_value['maintenance'][item]
        if 'monthly_production' in ms_value and len(ms_value['monthly_production']) > 0:
            ms_value['zhcn_monthly'] = '§E产出：§!'
            for item in ms_value['monthly_production']:
                if item in pdx_resource:
                    ms_value['zhcn_monthly'] += '£' + pdx_resource[item] + \
                                                ms_value['monthly_production'][item]
        if 'entity_offset' in ms_value and len(ms_value['entity_offset']) > 0:
            ms_value['zhcn_offset'] = '§E模型偏移量：§!'
            for item in ms_value['entity_offset']:
                # if item in fool_donkey_dict_resource:
                ms_value['zhcn_offset'] += item + '=' + ms_value['entity_offset'][item] + '，'
            ms_value['zhcn_offset'] = ms_value['zhcn_offset'][0:-1]
        if 'upgrade_from' in ms_value and len(ms_value['upgrade_from']) > 0:
            for i in range(len(ms_value['upgrade_from'])):
                if ms_value['upgrade_from'][i] in data:
                    if not ('upgrade' in data[ms_value['upgrade_from'][i]]):
                        data[ms_value['upgrade_from'][i]]['upgrade'] = []
                    data[ms_value['upgrade_from'][i]]['upgrade'].append(ms_name)
        if 'placement_rules' in ms_value and len(ms_value['placement_rules']) > 0:
            logic_it('placement_rules', ms_value, i18n_zhcn_map, i18n_en_map, '放置规则', data)
        if 'on_build_start' in ms_value and len(ms_value['on_build_start']) > 0:
            logic_it('on_build_start', ms_value, i18n_zhcn_map, i18n_en_map, '开始建造事件', data)
        if 'on_build_cancel' in ms_value and len(ms_value['on_build_cancel']) > 0:
            logic_it('on_build_cancel', ms_value, i18n_zhcn_map, i18n_en_map, '取消建造事件', data)
        if 'on_build_complete' in ms_value and len(ms_value['on_build_complete']) > 0:
            logic_it('on_build_complete', ms_value, i18n_zhcn_map, i18n_en_map, '建造完毕事件', data)
        if 'entity' in ms_value:
            ms_value['entity'] = ms_value['entity'].replace('"', '')
        if 'construction_entity' in ms_value:
            ms_value['construction_entity'] = ms_value['construction_entity'].replace('"', '')
        if ms_name[0:10] == 'ring_world':
            ms_value['icon'] = 'tech_mega_engineering'
            ms_value['type'] = 'ring_world'
        elif ms_name[0:12] == 'dyson_sphere':
            ms_value['icon'] = 'tech_dyson_sphere'
            ms_value['type'] = 'dyson_sphere'
        elif ms_name[0:10] == 'think_tank':
            ms_value['icon'] = 'tech_think_tank'
            ms_value['type'] = 'think_tank'
        elif ms_name[0:7] == 'spy_orb':
            ms_value['icon'] = 'tech_spy_orb'
            ms_value['type'] = 'spy_orb'
        elif ms_name[0:7] == 'gateway':
            ms_value['icon'] = 'tech_gateway_activation'
            ms_value['type'] = 'gateway'
        elif ms_name[0:7] == 'habitat':
            ms_value['icon'] = 'tech_habitat'
            ms_value['type'] = 'habitat'
        if ms_name + '_megastructure_details' in i18n_zhcn_map:
            ms_value['megastructure_details'] = i18n_zhcn_map[ms_name + '_megastructure_details']
        if ms_name + '_construction_info_delayed' in i18n_zhcn_map:
            ms_value['construction_info_delayed'] = i18n_zhcn_map[ms_name + '_construction_info_delayed']
    return data


def casus_belli_refinery(data, i18n_zhcn_map, i18n_en_map, war_goals):
    for cb_name, cb_value in data.items():
        if 'zhcn_name' in cb_value:
            name = 'casus_belli_' + cb_value['zhcn_name']
            cb_value['zhcn_name'], cb_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
            desc = name + '_acquire_hint'
            cb_value['zhcn_desc'], cb_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if 'is_valid' in cb_value:
            logic_it('is_valid', cb_value, i18n_zhcn_map, i18n_en_map, '条件', data)
            cb_value['is_valid_logic'] = re.sub(r'与§H自己§!相同', r'与§H防御方§!相同', cb_value['is_valid_logic'])
            cb_value['is_valid_logic'] = re.sub(r'与§H自己§!不同', r'与§H防御方§!不同', cb_value['is_valid_logic'])
        cb_value['wargoals'] = []
    for item in war_goals:
        if 'casus_belli' in item:
            for cb in data:
                if data[cb]['key'] == item['casus_belli']:
                    data[cb]['war_goals'].append(item['key'])
    return data


def policies_refinery(data, i18n_zhcn_map, i18n_en_map):
    for policies_name, policies_value in data.items():
        name = 'policy_' + policies_value['key']
        policies_value['zhcn_name'], policies_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        policies_value['zhcn_desc'], policies_value['en_desc'] = zhcn(name + '_desc', i18n_zhcn_map, i18n_en_map, True)
        if 'option' in policies_value:
            for options in policies_value['option']:
                name = options['name'].replace('"', '')
                desc = options['name'].replace('"', '') + '_desc'
                options['zhcn_name'], options['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
                options['zhcn_desc'], options['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
                if 'valid' in options:
                    logic_it('valid', options, i18n_zhcn_map, i18n_en_map, '条件', data)
                if 'AI_weight' in options:
                    logic_it('AI_weight', options, i18n_zhcn_map, i18n_en_map, 'AI权重', data)
                if 'on_enabled' in options:
                    logic_it('on_enabled', options, i18n_zhcn_map, i18n_en_map, '开启后', data)
                if 'on_disabled' in options:
                    logic_it('on_disabled', options, i18n_zhcn_map, i18n_en_map, '禁用后', data)
                if 'modifier' in options:
                    if len(options['modifier']) == 0:
                        options.pop('modifier')
                    else:
                        Danteng.log('\n选项：' + options['zhcn_name'] + '的modifier：' + 'modifier')
                        options['zhcn_modifier'] = modifier_processor(options['modifier'], i18n_zhcn_map, i18n_en_map)

    return data


def star_classes_data_refinery(data, i18n_zhcn_map, i18n_en_map, planet_classes):
    new_data = {}
    for sc_name, sc_value in data.items():
        if not ('rl_' in sc_name):
            new_data[sc_name] = sc_value
    data = new_data
    for sc_name, sc_value in data.items():
        key = ''
        if 'planet' in sc_value and 'key' in sc_value['planet']:
            sc_value['icon'] = sc_value['planet']['key']
            key = sc_value['planet']['key']
        planets = ['pc_continental', 'pc_desert', 'pc_tropical', 'pc_arid', 'pc_ocean', 'pc_tundra', 'pc_arctic',
                   'pc_alpine', 'pc_savannah', ]
        has_habitable = False
        spawn_mult = '1.0'
        for planet in planets:
            if planet in sc_value:
                if not has_habitable:
                    spawn_mult = sc_value[planet]['spawn_odds']
                    has_habitable = True
                elif sc_value[planet]['spawn_odds'] != spawn_mult:
                    Danteng.log('注意！此处不相等')
        if has_habitable:
            sc_value['habitable'] = '§E宜居行星生成概率修正系数：§!\\n' + spawn_mult
            if key in planet_classes:
                planet_classes[key]['habitable_odds'] = '宜居行星概率修正：' + spawn_mult
        if 'num_planets' in sc_value:
            if key in planet_classes:
                planet_classes[key]['desc_detail'] += '星系内行星数' + sc_value['num_planets']['min'] + '~' \
                                                      + sc_value['num_planets']['max']
        if 'zhcn_modifier' in sc_value:
            if key in planet_classes:
                effect = zhcn('effects_on_system', i18n_zhcn_map, i18n_en_map)[0]
                planet_classes[key]['effect'] = effect + '\\n' + sc_value['zhcn_modifier']
                planet_classes[key]['zhcn_desc'] += '\\n\\n' + planet_classes[key]['effect']
                sc_value['zhcn_modifier'] = zhcn('environmental_hazards', i18n_zhcn_map, i18n_en_map)[0] + sc_value[
                    'zhcn_modifier']
        if 'spawn_odds' in sc_value:
            if key in planet_classes:
                planet_classes[key]['spawn_odds'] = sc_value['spawn_odds']
    return data


def armies_refinery(data):
    for armies_name, armies_value in data.items():
        if ('cost' in armies_value and len(armies_value['cost']) > 0) or 'time' in armies_value:
            armies_value['zhcn_cost'] = '§E花费：§!'
            if 'cost' in armies_value:
                for item in armies_value['cost']:
                    if item in pdx_resource:
                        armies_value['zhcn_cost'] += '£' + pdx_resource[item] + armies_value['cost'][item]
            if 'time' in armies_value:
                armies_value['zhcn_cost'] += '£' + pdx_resource['time'] + armies_value['time']
        if 'icon_frame' in armies_value:
            armies_value['icon'] = 'army_icon_' + armies_value['icon_frame']
        base_health = 200.0
        base_damage_min = 1.5
        base_damage_max = 3.0
        base_morale = 200.0
        morale_damage_mult = 1.0
        attrs = {'health', 'damage', 'morale', 'morale_damage', 'collateral_damage', 'war_exhaustion'}
        for attr in attrs:
            if not (attr in armies_value):
                armies_value[attr] = '0'
        armies_value['max_health'] = '%.2f' % (base_health * float(armies_value['health']))
        armies_value['min_damage'] = base_damage_min * float(armies_value['damage'])
        armies_value['max_damage'] = base_damage_max * float(armies_value['damage'])
        armies_value['max_morale'] = '%.2f' % (base_morale * float(armies_value['morale']))
        armies_value['min_morale_damage'] = '%.2f' % (armies_value['min_damage'] * morale_damage_mult * float(
            armies_value['morale_damage']))
        armies_value['max_morale_damage'] = '%.2f' % (armies_value['max_damage'] * morale_damage_mult * float(
            armies_value['morale_damage']))
        armies_value['min_damage'] = '%.2f' % armies_value['min_damage']
        armies_value['max_damage'] = '%.2f' % armies_value['max_damage']
        if armies_value['collateral_damage'] != '0':
            armies_value['collateral'] = '%g%%' % (float(armies_value['collateral_damage']) * 100)

    return data


def bombardment_stances_refinery(data, i18n_zhcn_map, i18n_en_map):
    for bs_name, bs_value in data.items():
        if 'trigger' in bs_value:
            logic_it('trigger', bs_value, i18n_zhcn_map, i18n_en_map, '允许开启条件', data)
        if 'icon_frame' in bs_value:
            if bs_value['icon_frame'] == '1':
                bs_value['icon'] = 'fleet_task_ground_support_selective'
            elif bs_value['icon_frame'] == '2':
                bs_value['icon'] = 'fleet_task_ground_support_indiscriminate'
            elif bs_value['icon_frame'] == '3':
                bs_value['icon'] = 'fleet_task_ground_support_armageddon'
            elif bs_value['icon_frame'] == '4':
                bs_value['icon'] = 'fleet_task_ground_support_raiding'
        name = 'bombardment_' + bs_value['key']
        bs_value['zhcn_name'], bs_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        bs_value['zhcn_desc'], bs_value['en_desc'] = zhcn(name + '_desc', i18n_zhcn_map, i18n_en_map, True)
    return data


def personalities_refinery(data, i18n_zhcn_map, i18n_en_map):
    behaviour = {}
    for p_name, p_value in data.items():
        name = 'personality_' + p_value['key']
        desc = name + '_desc'
        p_value['zhcn_name'], p_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        p_value['zhcn_desc'], p_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if 'behaviour' in p_value:
            p_value['zhcn_behaviour'] = '§E行为模式：§!\\n'
            for name, value in p_value['behaviour'].items():
                string = 'personality_type_' + name
                p_value['zhcn_behaviour'] += zhcn(string, i18n_zhcn_map, i18n_en_map)[0] + '：'
                if value == 'yes':
                    p_value['zhcn_behaviour'] += '§H是§!\\n'
                else:
                    p_value['zhcn_behaviour'] += '§H否§!\\n'
        if 'weapon_preferences' in p_value:
            p_value['zhcn_weapon'] = zhcn(p_value['weapon_preferences'], i18n_zhcn_map, i18n_en_map)[0]
        behaviour[p_name] = p_value['behaviour']
    save_data('personalities_behaviour', behaviour)
    return behaviour


def pft_refinery(data, i18n_zhcn_map, i18n_en_map):
    for pft_name, pft_value in data.items():
        name = 'pft_' + pft_value['key']
        desc = 'pft_' + pft_value['key'] + '_desc'
        pft_value['zhcn_name'], pft_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        pft_value['zhcn_desc'], pft_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if 'election_header' in pft_value:
            pft_value['election_header'] = pft_value['election_header'].replace('"', '')
        if 'is_potential' in pft_value:
            logic_it('is_potential', pft_value, i18n_zhcn_map, i18n_en_map, '允许开启条件', data)
        # if 'parameters' in pft_value:
        #     logic_it('parameters', pft_value, i18n_zhcn_map, i18n_en_map, '参数要求', data)
        if 'can_join_faction' in pft_value:
            logic_it('can_join_faction', pft_value, i18n_zhcn_map, i18n_en_map, '加入派系要求', data)
        if 'attraction' in pft_value:
            logic_it('attraction', pft_value, i18n_zhcn_map, i18n_en_map, '吸引力修正', data)
        if 'leader' in pft_value:
            logic_it('leader', pft_value, i18n_zhcn_map, i18n_en_map, '派系领导人修正', data)
        if 'demand' in pft_value:
            for i in range(len(pft_value['demand'])):
                pft_value['demand'][i]['title'] = pft_value['demand'][i]['title'].replace('"', '')
                pft_value['demand'][i]['unfulfilled_title'] = pft_value['demand'][i]['unfulfilled_title'].replace('"',
                                                                                                                  '')
                pft_value['demand'][i]['desc'] = pft_value['demand'][i]['desc'].replace('"', '')
                pft_value['demand'][i]['zhcn_name'] = zhcn(pft_value['demand'][i]['title'], i18n_zhcn_map,
                                                           i18n_en_map)[0]
                pft_value['demand'][i]['un_name'] = zhcn(pft_value['demand'][i]['unfulfilled_title'], i18n_zhcn_map,
                                                         i18n_en_map)[0]
                pft_value['demand'][i]['zhcn_name'] = zhcn(pft_value['demand'][i]['zhcn_name'], i18n_zhcn_map,
                                                           i18n_en_map)[0] \
                    .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                    .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                    .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                    .replace('[Root.Owner.GetAdj]', '帝国') \
                    .replace('[Root.Owner.GetName]', '帝国') \
                    .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')
                pft_value['demand'][i]['un_name'] = zhcn(pft_value['demand'][i]['un_name'], i18n_zhcn_map, i18n_en_map)[
                    0] \
                    .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                    .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                    .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                    .replace('[Root.Owner.GetAdj]', '帝国') \
                    .replace('[Root.Owner.GetName]', '帝国') \
                    .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')
                pft_value['demand'][i]['desc'] = zhcn(pft_value['demand'][i]['desc'], i18n_zhcn_map, i18n_en_map)[0] \
                    .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                    .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                    .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                    .replace('[Root.Owner.GetAdj]', '帝国') \
                    .replace('[Root.Owner.GetName]', '帝国') \
                    .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')

                if 'potential' in pft_value['demand'][i]:
                    logic_it('potential', pft_value['demand'][i], i18n_zhcn_map, i18n_en_map, '基础要求', data)
                if 'trigger' in pft_value['demand'][i]:
                    logic_it('trigger', pft_value['demand'][i], i18n_zhcn_map, i18n_en_map, '触发条件', data)
        if 'on_create' in pft_value:
            logic_it('on_create', pft_value, i18n_zhcn_map, i18n_en_map, '建立派系时', data)
        if 'on_destroy' in pft_value:
            logic_it('on_destroy', pft_value, i18n_zhcn_map, i18n_en_map, '派系解散时', data)
        if 'actions' in pft_value:
            for item in pft_value['actions']:
                pft_value['actions'][item]['zhcn_name'] = zhcn(pft_value['actions'][item]['title'].replace('"', ''),
                                                               i18n_zhcn_map, i18n_en_map)[0]
                if 'cost' in pft_value['actions'][item]:
                    pft_value['actions'][item]['zhcn_cost'] = ''
                    for cost in pft_value['actions'][item]['cost']:
                        if cost in pdx_resource:
                            pft_value['actions'][item]['zhcn_cost'] += '£' + pdx_resource[cost] + \
                                                                       pft_value['actions'][item]['cost'][cost]
                if 'potential' in pft_value['actions'][item]:
                    logic_it('potential', pft_value['actions'][item], i18n_zhcn_map, i18n_en_map, '基础要求', data)
                if 'valid' in pft_value['actions'][item]:
                    logic_it('valid', pft_value['actions'][item], i18n_zhcn_map, i18n_en_map, '条件', data)
                if 'effect' in pft_value['actions'][item]:
                    logic_it('effect', pft_value['actions'][item], i18n_zhcn_map, i18n_en_map, '效果', data)
                if 'ai_weight' in pft_value['actions'][item]:
                    logic_it('ai_weight', pft_value['actions'][item], i18n_zhcn_map, i18n_en_map, 'AI权重', data)
    return data


def subjects_refinery(data, i18n_zhcn_map, i18n_en_map):
    for name, value in data.items():
        name = 'subject_' + value['key']
        desc = 'subject_desc_' + value['key']
        value['zhcn_name'], value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        value['zhcn_desc'], value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if 'subject_tax_rate' in value:
            value['zhcn_tax_rate'] = ''
            for item in value['subject_tax_rate']:
                if item in pdx_resource:
                    num = float(value['subject_tax_rate'][item])
                    para_str = '%g%%' % (num * 100)
                    value['zhcn_tax_rate'] += '£' + pdx_resource[item] + para_str + '，'
            value['zhcn_tax_rate'] = value['zhcn_tax_rate'][0:-1]
        if 'can_switch_to' in value:
            find = re.findall(r'[A-Za-z]+', value['can_switch_to'][0])
            if find:
                value['can_switch_to'] = find
        if 'effect' in value:
            logic_it('effect', value, i18n_zhcn_map, i18n_en_map, '效果', data)
        if 'become_vassal' in value:
            logic_it('become_vassal', value, i18n_zhcn_map, i18n_en_map, '成为附庸的条件', data)
        if 'potential_logic' in value:
            value['potential_logic'] = re.sub(r'who§H来自§!', r'与前者相比', value['potential_logic'])
        if 'effect_logic' in value:
            value['effect_logic'] = re.sub(r'who§H来自§!', r'与前者相比', value['effect_logic'])
        if 'become_vassal_logic' in value:
            value['become_vassal_logic'] = re.sub(r'who§H来自§!', r'与前者相比', value['become_vassal_logic'])
        if 'tech_cost_mult' in value:
            num = float(value['tech_cost_mult'])
            value['tech_cost'] = '%+g%%' % (num * 100)
        if value['key'] == 'satrapy':
            value['zhcn_name'], value['en_name'] = zhcn('satrapy_of_horde', i18n_zhcn_map, i18n_en_map)
            value['zhcn_desc'], value['en_desc'] = zhcn('satrapy_of_horde_desc', i18n_zhcn_map, i18n_en_map, True)
    return data


def war_goals_refinery(data, i18n_zhcn_map, i18n_en_map):
    for wg_name, wg_value in data.items():
        name = 'war_goal_' + wg_value['key']
        desc = 'war_goal_' + wg_value['key'] + '_desc'
        wg_value['zhcn_name'], wg_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        wg_value['zhcn_desc'], wg_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if 'on_accept' in wg_value:
            logic_it('on_accept', wg_value, i18n_zhcn_map, i18n_en_map, '达成战争目标时', data)
            wg_value['on_accept_logic'] = wg_value['on_accept_logic'] \
                .replace('[Root.GetName]', '进攻方') \
                .replace('[From.GetName]', '防御方') \
                .replace('[Root.GetAdj]', '进攻方的')
        if 'on_status_quo' in wg_value:
            logic_it('on_status_quo', wg_value, i18n_zhcn_map, i18n_en_map, '白和平时', data)
            wg_value['on_status_quo_logic'] = wg_value['on_status_quo_logic'] \
                .replace('[Root.GetName]', '进攻方') \
                .replace('[From.GetName]', '防御方') \
                .replace('[Root.GetAdj]', '进攻方的')
        if 'on_wargoal_set' in wg_value:
            logic_it('on_wargoal_set', wg_value, i18n_zhcn_map, i18n_en_map, '设定战争目标时', data)
            wg_value['on_wargoal_set_logic'] = wg_value['on_wargoal_set_logic'] \
                .replace('[Root.GetName]', '进攻方') \
                .replace('[From.GetName]', '防御方') \
                .replace('[Root.GetAdj]', '进攻方的')
        if 'possible' in wg_value:
            wg_value.pop('possible_desc')
            logic_it('possible', wg_value, i18n_zhcn_map, i18n_en_map, i18n_zhcn_map['REQUIREMENTS'], data)
    return data


def achievements_refinery(data, i18n_zhcn_map, i18n_en_map):
    refined_data = {}
    for name, value in data.items():
        value['key'] = name
        if 'id' in value:
            value['_index'] = value['id']
        if 'possible' in value:
            logic_it('possible', value, i18n_zhcn_map, i18n_en_map, i18n_zhcn_map['REQUIREMENTS'], data)
        if 'happened' in value:
            logic_it('happened', value, i18n_zhcn_map, i18n_en_map, '完成成就所需条件', data)
    refined_data.update(data)
    return refined_data


def starbase_buildings_refinery(data, i18n_zhcn_map, i18n_en_map):
    for sb_name, sb_value in data.items():
        name = 'sm_' + sb_value['key']
        desc = 'sm_' + sb_value['key'] + '_desc'
        sb_value['zhcn_name'], sb_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        sb_value['zhcn_desc'], sb_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        icon_dict = {'cost', 'produced_resources', 'upkeep_resources'}
        for item in icon_dict:
            if item in sb_value:
                temp_str = ''
                for res in sb_value[item]:
                    if res in pdx_resource:
                        res_icon = '£' + pdx_resource[res]
                    else:
                        res_icon = '£' + res
                    temp_str += res_icon + ' ' + sb_value[item][res] + ' '
                    sb_value['zhcn_' + item] = temp_str
        if 'show_in_tech' in sb_value:
            sb_value['prerequisites'] = ['']
            sb_value['prerequisites'][0] = sb_value['show_in_tech'].replace('"', '')
        if 'possible' in sb_value:
            sb_value.pop('possible_desc')
            logic_it('possible', sb_value, i18n_zhcn_map, i18n_en_map, i18n_zhcn_map['REQUIREMENTS'], data)
        if 'custom_tooltip' in sb_value:
            sb_value['zhcn_tip'] = zhcn(sb_value['custom_tooltip'], i18n_zhcn_map, i18n_en_map)[0]
        if 'equipped_component' in sb_value:
            sb_value['equipped_component'] = sb_value['equipped_component'].replace('"', '')
    return data


def starbase_levels_refinery(data, i18n_zhcn_map, i18n_en_map):
    for sl_name, sl_value in data.items():
        if 'ship_size' in sl_value:
            sl_value['zhcn_name'], sl_value['en_name'] = zhcn(sl_value['ship_size'], i18n_zhcn_map, i18n_en_map)
        if 'level_weight' in sl_value:
            icon_index = int(sl_value['level_weight']) + 1
            if icon_index > 5:
                icon_index = 5
            sl_value['icon'] = 'starbase_' + str(icon_index)
    return data


def starbase_modules_refinery(data, i18n_zhcn_map, i18n_en_map):
    for sm_name, sm_value in data.items():
        name = 'sm_' + sm_value['key']
        desc = 'sm_' + sm_value['key'] + '_desc'
        sm_value['zhcn_name'], sm_value['en_name'] = zhcn(name, i18n_zhcn_map, i18n_en_map)
        sm_value['zhcn_desc'], sm_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        icon_dict = {'cost', 'produced_resources', 'upkeep_resources'}
        for item in icon_dict:
            if item in sm_value:
                temp_str = ''
                for res in sm_value[item]:
                    if res in pdx_resource:
                        res_icon = '£' + pdx_resource[res]
                    else:
                        res_icon = '£' + res
                    temp_str += res_icon + ' ' + sm_value[item][res] + ' '
                    sm_value['zhcn_' + item] = temp_str
        if 'section' in sm_value:
            sm_value['section'] = sm_value['section'].replace('"', '')
        if 'possible' in sm_value:
            sm_value.pop('possible_desc')
            logic_it('possible', sm_value, i18n_zhcn_map, i18n_en_map, i18n_zhcn_map['REQUIREMENTS'], data)
        if 'show_in_tech' in sm_value:
            sm_value['prerequisites'] = ['']
            sm_value['prerequisites'][0] = sm_value['show_in_tech'].replace('"', '')
        if 'triggered_country_modifier' in sm_value:
            logic_it('triggered_country_modifier', sm_value, i18n_zhcn_map, i18n_en_map, '额外国家修正', data)
        if 'produced_resource_trigger' in sm_value:
            logic_it('produced_resource_trigger', sm_value, i18n_zhcn_map, i18n_en_map, '额外产出修正', data)
        if 'icon' not in sm_value:
            sm_value['icon'] = 'starbase_' + sm_value['key']
    return data


def component_sets_refinery(data, icons):
    refined_data = OrderedDict()
    for cs_name, cs_value in data.items():
        name = cs_value['key'].replace('"', '')
        refined_data[name] = {}
        refined_data[name]['key'] = name
        icon = cs_value['icon'].replace('"', '')
        refined_data[name]['icon'] = icon
        if icon in icons:
            refined_data[name]['icon'] = icons[icon]['icon']
    return refined_data


def component_templates_refinery(data, i18n_zhcn_map, i18n_en_map, icons, component_sets, component_add):
    refined_data = OrderedDict()
    for ct_name, ct_value in data.items():
        key = ct_value['key'].replace('"', '')
        ct_value['key'] = key
        ct_value['zhcn_name'], ct_value['en_name'] = zhcn(key, i18n_zhcn_map, i18n_en_map)
        ct_value['zhcn_desc'], ct_value['en_desc'] = zhcn(key + '_DESC', i18n_zhcn_map, i18n_en_map, True)
        if 'component_set' in ct_value:
            ct_value['component_set'] = ct_value['component_set'].replace('"', '')

        if 'icon' in ct_value:
            icon = ct_value['icon'].replace('"', '')
            Danteng.log('图标：' + ct_value['icon'])
            if icon in icons:
                ct_value['icon'] = icons[icon]['icon']
                Danteng.log('修正图标：' + ct_value['icon'])

        if 'power' in ct_value:
            if type(ct_value['power']) != str:
                ct_value['power'] = ct_value['power'][0]
            ct_value['power'] = int(ct_value['power'])
        if 'entity' in ct_value:
            ct_value['entity'] = ct_value['entity'].replace('"', '')
        if 'projectile_gfx' in ct_value:
            ct_value['projectile_gfx'] = ct_value['projectile_gfx'].replace('"', '')
        if 'ship_behavior' in ct_value:
            ct_value['ship_behavior'] = ct_value['ship_behavior'].replace('"', '')
        if 'planet_destruction_gfx' in ct_value:
            ct_value['planet_destruction_gfx'] = ct_value['planet_destruction_gfx'].replace('"', '')
        if 'class_restriction' in ct_value:
            find = re.findall(r'(\S+)', ct_value['class_restriction'][0])
            if find:
                ct_value['class_restriction'] = find
        if 'size_restriction' in ct_value:
            find = re.findall(r'(\S+)', ct_value['size_restriction'][0])
            if find:
                ct_value['size_restriction'] = find
        if 'instruction' in ct_value:
            find = re.findall(r'(\S+)', ct_value['instruction'])
            if find:
                ct_value['instruction'] = find
            for i in range(len(ct_value['instruction'])):
                ct_value['instruction'][i] = zhcn(ct_value['instruction'][i], i18n_zhcn_map, i18n_en_map)[0]
        if 'tags' in ct_value:
            find = re.findall(r'(\S+)', ct_value['tags'][0])
            if find:
                ct_value['tags'] = find
        if 'upgrades_to' in ct_value:
            upgrade = ['']
            upgrade[0] = ct_value['upgrades_to'].replace('"', '')
            ct_value['upgrades_to'] = upgrade
        if 'damage' in ct_value:
            ct_value['min_damage'] = ct_value['damage']['min']
            ct_value['max_damage'] = ct_value['damage']['max']
        if 'hostile_aura' in ct_value:
            # ct_value['icon'] = 'GFX_ship_part_' + ct_value['hostile_aura']['name']
            # if ct_value['icon'] in icons:
            #     ct_value['icon'] = icons[ct_value['icon']]['icon']
            if 'name' in ct_value['hostile_aura']:
                ct_value['hostile_aura']['name'] = ct_value['hostile_aura']['name'].replace('"', '')
                ct_value['hostile_aura']['zhcn_name'], ct_value['hostile_aura']['en_name'] = \
                    zhcn(ct_value['hostile_aura']['name'], i18n_zhcn_map, i18n_en_map)
            if 'modifier' in ct_value['hostile_aura']:
                Danteng.log('\n' + ct_value['hostile_aura']['zhcn_name'] + '的modifier：' + 'modifier')
                ct_value['hostile_aura']['zhcn_modifier'] = modifier_processor(
                    ct_value['hostile_aura']['modifier'], i18n_zhcn_map, i18n_en_map)
        if 'friendly_aura' in ct_value:
            # ct_value['icon'] = 'ship_part_aura_nanobot'
            if 'name' in ct_value['friendly_aura']:
                ct_value['friendly_aura']['name'] = ct_value['friendly_aura']['name'].replace('"', '')
                ct_value['friendly_aura']['zhcn_name'], ct_value['friendly_aura']['en_name'] = \
                    zhcn(ct_value['friendly_aura']['name'], i18n_zhcn_map, i18n_en_map)
            if 'modifier' in ct_value['friendly_aura']:
                Danteng.log('\n' + ct_value['friendly_aura']['zhcn_name'] + '的modifier：' + 'modifier')
                ct_value['friendly_aura']['zhcn_modifier'] = modifier_processor(
                    ct_value['friendly_aura']['modifier'], i18n_zhcn_map, i18n_en_map)
        if 'size' in ct_value:
            ct_value['size'] = ct_value['size'].lower()
        if 'component_set' not in ct_value:
            ct_value['component_set'] = ''
        if 'class_restriction' in ct_value:
            ct_value['zhcn_class_restriction'] = ''
            for i in range(len(ct_value['class_restriction'])):
                ct_value['zhcn_class_restriction'] = ct_value['zhcn_class_restriction'] + \
                                                     zhcn(ct_value['class_restriction'][i], i18n_zhcn_map, i18n_en_map)[
                                                         0] + '，'
            ct_value['zhcn_class_restriction'] = ct_value['zhcn_class_restriction'][0:-1]
        if ct_value['icon'] == 'GFX_ship_part_sensor':
            ct_value['icon'] = 'ship_part_empty_ftl_drive'

        # 给蠢驴分个类
        if 'tags' in ct_value and 'weapon_type_strike_craft' in ct_value['tags']:
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'H'
        elif ct_value['size'] == 'point_defence':
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'P'
        elif ct_value['size'] == 'planet_killer':
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'W'
        elif ct_value['size'] == 'torpedo':
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'G'
        elif ct_value['size'] == 'titanic':
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'T'
        elif ct_value['size'] == 'extra_large':
            ct_value['category'] = 'weapon'
            ct_value['slot'] = 'X'
        elif ct_value['size'] == 'aux':
            ct_value['category'] = 'utility'
            ct_value['slot'] = 'A'
        elif ct_value['component_set'] == 'power_core':
            ct_value['category'] = 'power_core'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'ftl_components':
            ct_value['category'] = 'ftl_components'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'thruster_components':
            ct_value['category'] = 'thruster_components'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'sensor_components':
            ct_value['category'] = 'sensor_components'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'combat_computers':
            ct_value['category'] = 'combat_computers'
            ct_value['slot'] = ''
        elif 'aura_components' in ct_value['component_set']:
            ct_value['category'] = 'aura_components'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'ftl_inhibitor':
            ct_value['category'] = 'ftl_inhibitor'
            ct_value['slot'] = ''
        elif 'type' in ct_value and (ct_value['type'] == 'instant' or ct_value['type'] == 'missile'):
            ct_value['category'] = 'weapon'
            if ct_value['size'] == 'large':
                ct_value['slot'] = 'L'
            elif ct_value['size'] == 'medium':
                ct_value['slot'] = 'M'
            elif ct_value['size'] == 'small':
                ct_value['slot'] = 'S'
            else:
                ct_value['slot'] = ''
        elif 'STARBASE_AURA' in ct_value['key']:
            ct_value['category'] = 'aura_components'
            ct_value['slot'] = ''
        elif ct_value['component_set'] == 'ENIGMATIC_DISRUPTION_FIELD':
            ct_value['category'] = 'aura_components'
            ct_value['slot'] = ''
        elif ct_value['key'] == 'STELLARITE_COMBAT_COMPUTER':
            ct_value['category'] = 'combat_computers'
            ct_value['slot'] = ''
        else:
            ct_value['category'] = 'utility'
            if ct_value['size'] == 'large':
                ct_value['slot'] = 'L'
            elif ct_value['size'] == 'medium':
                ct_value['slot'] = 'M'
            elif ct_value['size'] == 'small':
                ct_value['slot'] = 'S'
            else:
                ct_value['slot'] = ''
        if 'ai_tags' in ct_value:
            ct_value['ai_task'] = ''
            for i in range(len(ct_value['ai_tags'])):
                ct_value['ai_task'] += zhcn(ct_value['ai_tags'][i], i18n_zhcn_map, i18n_en_map)[0] + ','
            ct_value['ai_task'] = ct_value['ai_task'][0:-1]
        if 'instruction' in ct_value:
            ct_value['zhcn_instruction'] = ''
            for i in range(len(ct_value['instruction'])):
                ct_value['zhcn_instruction'] += zhcn(ct_value['instruction'][i], i18n_zhcn_map, i18n_en_map)[0] + ','
            ct_value['zhcn_instruction'] = ct_value['zhcn_instruction'][0:-1]
        if 'component_set' in ct_value:
            ct_value['sets'] = zhcn(ct_value['component_set'], i18n_zhcn_map, i18n_en_map)[0]
        if ct_value['key'] in component_add:
            ct_value.update(component_add[ct_value['key']])
        nums = ['cost', 'power', 'min_damage', 'max_damage', 'hull_damage', 'shield_damage', 'shield_penetration',
                'armor_damage', 'armor_penetration', 'min_windup', 'max_windup', 'cooldown', 'range', 'accuracy',
                'tracking', 'missile_speed', 'missile_evasion', 'missile_shield', 'missile_armor', 'missile_health',
                'missile_retarget_range']
        for i in range(len(nums)):
            if nums[i] in ct_value:
                ct_value[nums[i]] = float(ct_value[nums[i]])
        refined_data[ct_value['key']] = ct_value
    # 武器计算
    # power
    # cost
    # damage =  min_damage ~ max_damage
    # cd = (cooldown + (min_windup + max_windup) / 2) / 10
    # accuracy
    # tracking
    # range
    # average = (min_damage + max_damage) / 2 / cd * accuracy
    # (1 + 1700) / 2 / 8.10 * 1 = 105
    # 假设对面闪避20%，你索敌10%，命中70%，索敌压制闪避，他天然的闪避变成了10%，不闪避的概率为90%，在这个90%中间有70%是你命中的，也就是你最终的命中为63%
    # 多余能量：(extra_energy / energy /10)
    # 96 454 550,96/550=0.1745454545, 1%
    # 382 1688 550,382/550=0.694545454, 6%
    # 400 18    22.222222=200/9           160
    # 350 15    23.333333
    # 420 18    23.333333    CMP_TT_SC_SPEED
    return refined_data


def ship_behaviors_refinery(data, i18n_zhcn_map, i18n_en_map):
    refined_data = OrderedDict()
    for sb_name, sb_value in data.items():
        key = sb_value['key'].replace('"', '')
        sb_value['key'] = key
        if 'desc' in sb_value:
            desc = sb_value['desc'].replace('"', '')
            sb_value['zhcn_desc'], sb_value['en_desc'] = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
        if key == 'ship_behavior_fighters_behavior':
            sb_value['zhcn_desc'] = '§H战斗机模式§!'
            sb_value['en_desc'] = '§HFighters behavior§!'
        elif key == 'ship_behavior_bombers_behavior':
            sb_value['zhcn_desc'] = '§H轰炸机模式§!'
            sb_value['en_desc'] = '§HBombers behavior§!'
        sb_value['zhcn_name'] = re.findall(r'§H(.*?)§', sb_value['zhcn_desc'])[0]
        if sb_value['zhcn_name'][-1] == '：':
            sb_value['zhcn_name'] = sb_value['zhcn_name'][0:-1]
        sb_value['en_name'] = re.findall(r'§H(.*?)§', sb_value['en_desc'])[0]
        if sb_value['en_name'][-1] == ':':
            sb_value['en_name'] = sb_value['en_name'][0:-1]
        refined_data[sb_value['key']] = sb_value
    return refined_data


def ship_sizes_refinery(data, i18n_zhcn_map, i18n_en_map):
    for ss_name, ss_value in data.items():
        if 'graphical_culture' in ss_value:
            find = re.findall(r'\"(.*?)\"', ss_value['graphical_culture'][0])
            if find:
                ss_value['graphical_culture'] = find
        if 'pre_communications_name' in ss_value:
            ss_value['pre_communications_name'] = zhcn(ss_value['pre_communications_name'].replace('"', ''),
                                                       i18n_zhcn_map, i18n_en_map)[0]
        if 'class' in ss_value:
            ss_value['zhcn_class'] = zhcn(ss_value['class'], i18n_zhcn_map, i18n_en_map)[0]
        if 'construction_type' in ss_value:
            ss_value['zhcn_construction_type'] = zhcn(ss_value['construction_type'], i18n_zhcn_map, i18n_en_map)[0]
        if 'required_component_set' in ss_value:
            ss_value['zhcn_required_component_set'] = '§E需要组件：§!'
            if type(ss_value['required_component_set']) == str:
                ss_value['required_component_set'] = [ss_value['required_component_set']]
            for i in range(len(ss_value['required_component_set'])):
                ss_value['required_component_set'][i] = ss_value['required_component_set'][i].replace('"', '')
                ss_value['zhcn_required_component_set'] += zhcn(ss_value['required_component_set'][i], i18n_zhcn_map,
                                                                i18n_en_map)[0] + '，'
            ss_value['zhcn_required_component_set'] = ss_value['zhcn_required_component_set'][0:-1]
        if 'possible_starbase' in ss_value:
            logic_it('possible_starbase', ss_value, i18n_zhcn_map, i18n_en_map, '允许建造该型号舰船的恒星基地', data)
        if 'empire_limit' in ss_value:
            ss_value['zhcn_limit'] = '§E建造上限：§!\\n'
            if 'base' in ss_value['empire_limit']:
                ss_value['zhcn_limit'] += '※14基础值：§H' + ss_value['empire_limit']['base'] + '§!\\n'
            if 'naval_cap_div' in ss_value['empire_limit']:
                ss_value['zhcn_limit'] += '※14每§H' + ss_value['empire_limit']['naval_cap_div'] + \
                                          '§!海军容量可多建造一艘\\n'
            if 'max' in ss_value['empire_limit']:
                ss_value['zhcn_limit'] += '※14最大值：§H' + ss_value['empire_limit']['max'] + '§!\\n'
        if 'upkeep_override' in ss_value:
            ss_value['zhcn_upkeep'] = ''
            for item in ss_value['upkeep_override']:
                if item in pdx_resource and ss_value['upkeep_override'][item] != '0':
                    ss_value['zhcn_upkeep'] += '£' + pdx_resource[item] + \
                                               ss_value['upkeep_override'][item]
        if 'section_slots' in ss_value:
            ss_value['zhcn_section'] = '§E舰船区块：§!'
            temp = {}
            for section_name, section_value in ss_value['section_slots'].items():
                section_name = section_name.replace('"', '')
                ss_value['zhcn_section'] += '※14\\n§H' + zhcn(section_name, i18n_zhcn_map, i18n_en_map)[0] + \
                                            '§!，位置：§H'
                if type(section_value['locator']) == str:
                    section_value['locator'] = section_value['locator'].replace('"', '')
                    ss_value['zhcn_section'] += section_value['locator']
                else:
                    for i in range(len(section_value['locator'])):
                        section_value['locator'][i] = section_value['locator'][i].replace('"', '')
                        ss_value['zhcn_section'] += section_value['locator'][i] + '，'
                    ss_value['zhcn_section'] = ss_value['zhcn_section'][0:-1]
                ss_value['zhcn_section'] += '§!\\n'
                temp[section_name] = section_value
            ss_value['section_slots'] = temp
        if 'combat_disengage_chance' in ss_value:
            ss_value['combat_disengage_chance'] = float(ss_value['combat_disengage_chance'])
        if 'icon_frame' in ss_value and ss_value['icon_frame'] != '-1':
            ss_value['icon'] = 'ship_sizes_' + ss_value['icon_frame']
        else:
            ss_value['icon'] = 'ship_sizes_1'
        if 'acceleration' in ss_value and type(ss_value['acceleration']) == list:
            ss_value['acceleration'] = ss_value['acceleration'][len(ss_value['acceleration']) - 1]
    return data


def section_templates_refinery(data, i18n_zhcn_map, i18n_en_map):
    refined_data = OrderedDict()
    for st_name, st_value in data.items():
        st_value['key'] = st_value['key'].replace('"', '')
        st_value['zhcn_name'], st_value['en_name'] = zhcn(st_value['key'], i18n_zhcn_map, i18n_en_map, True)
        refined_data[st_value['key']] = st_value
        if 'ship_size' in st_value:
            if type(st_value['ship_size']) == str:
                st_value['ship_size'] = [st_value['ship_size']]
            st_value['zhcn_ship_size'] = '§E适用舰船类型：§!'
            for i in range(len(st_value['ship_size'])):
                st_value['zhcn_ship_size'] += zhcn(st_value['ship_size'][i], i18n_zhcn_map, i18n_en_map, True)[0] + '，'
            st_value['zhcn_ship_size'] = st_value['zhcn_ship_size'][0:-1]
        if st_value['zhcn_name'] == '':
            st_value['zhcn_name'] = '核心'
            st_value['en_name'] = 'core'
        if 'fits_on_slot' in st_value:
            if type(st_value['fits_on_slot']) == str:
                st_value['fits_on_slot'] = [st_value['fits_on_slot']]
            for i in range(len(st_value['fits_on_slot'])):
                st_value['fits_on_slot'][i] = st_value['fits_on_slot'][i].replace('"', '')
        if 'prerequisites' in st_value:
            find = re.findall(r'(\S+)', st_value['prerequisites'][0])
            if find:
                st_value['prerequisites'] = find
        if 'entity' in st_value:
            st_value['entity'] = st_value['entity'].replace('"', '')
        if 'component_slot' in st_value:
            if type(st_value['component_slot']) != list:
                st_value['component_slot'] = [st_value['component_slot']]
            st_value['slot_count'] = {'P': 0, 'S': 0, 'G': 0, 'M': 0, 'L': 0, 'H': 0, 'X': 0, 'T': 0, 'W': 0}
            for i in range(len(st_value['component_slot'])):
                if 'slot_type' in st_value['component_slot'][i] and \
                        st_value['component_slot'][i]['slot_type'] == 'weapon':
                    if st_value['component_slot'][i]['slot_size'] == 'point_defence':
                        st_value['slot_count']['P'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'small':
                        st_value['slot_count']['S'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'torpedo':
                        st_value['slot_count']['G'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'medium':
                        st_value['slot_count']['M'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'large':
                        st_value['slot_count']['L'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'strike_craft':
                        st_value['slot_count']['H'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'extra_large':
                        st_value['slot_count']['X'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'titanic':
                        st_value['slot_count']['T'] += 1
                    elif st_value['component_slot'][i]['slot_size'] == 'planet_killer':
                        st_value['slot_count']['W'] += 1
                for cs_name, cs_value in st_value['component_slot'][i].items():
                    Danteng.log(st_name + ' component_slot ' + cs_name + ': ')
                    if type(st_value['component_slot'][i][cs_name]) == str:
                        st_value['component_slot'][i][cs_name] = cs_value.replace('"', '')
    return refined_data


def events_refinery(data, i18n_zhcn_map, i18n_en_map, icons):
    refined_data = OrderedDict()
    temp = OrderedDict()
    for name, value in data.items():
        value['id'] = value['id'].replace('"', '')
        ids = value['id']
        value['key'] = ids
        if 'title' in value:
            value['title'] = value['title'].replace('"', '')
            value['zhcn_name'], value['en_name'] = zhcn(value['title'], i18n_zhcn_map, i18n_en_map, True)
            if 'desc' in value and type(value['desc']) == str:
                value['desc'] = value['desc'].replace('"', '')
                value['zhcn_desc'], value['en_desc'] = zhcn(value['desc'], i18n_zhcn_map, i18n_en_map, True)
            elif 'desc' in value and type(value['desc']) == list:
                value['zhcn_desc'] = []
                value['en_desc'] = []
                for i in range(len(value['desc'])):
                    if 'text' in value['desc'][i]:
                        desc = value['desc'][i]['text'].replace('"', '')
                    elif type(value['desc'][i]) == str:
                        desc = value['desc'][i].replace('"', '')
                    else:
                        if name not in temp:
                            temp[name] = OrderedDict()
                        temp[name][i] = value['desc'][i]
                        Danteng.log('未处理的事件描述：'+ ids)
                        desc = ''
                    zh_desc, en_desc = zhcn(desc, i18n_zhcn_map, i18n_en_map, True)
                    value['zhcn_desc'].append(zh_desc)
                    value['en_desc'].append(en_desc)
            else:
                value['zhcn_desc'], value['en_desc'] = zhcn(value['id'] + '.desc', i18n_zhcn_map, i18n_en_map, True)
        else:
            value['zhcn_name'] = '无标题'
            value['en_name'] = 'No Title'
            value['zhcn_desc'] = '无描述'
            value['en_desc'] = 'No Description'
        if 'picture' in value:
            if type(value['picture']) == str:
                value['picture'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', value['picture'].replace('"', ''))
                if value['picture'] in icons:
                    value['picture'] = icons[value['picture']]['icon']
            elif type(value['picture']) == list:
                for i in range(len(value['picture'])):
                    picture = value['picture'][i]['picture']
                    picture = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', picture.replace('"', ''))
                    if picture in icons:
                        value['picture'][i]['picture'] = icons[picture]['icon']
            else:
                z = 2
        option = []
        if 'option' in value:
            if type(value['option']) != list:
                option.append(value['option'])
            else:
                option = value['option']
            for i in range(len(option)):
                if 'name' in option[i]:
                    option[i]['name'] = option[i]['name'].replace('"', '')
                    option[i]['zhcn_name'], option[i]['en_name'] = zhcn(option[i]['name'], i18n_zhcn_map, i18n_en_map)
                    option[i]['zhcn_desc'], option[i]['zhcn_desc'] = zhcn(option[i]['name'] + '.tooltip', i18n_zhcn_map,
                                                                          i18n_en_map)
                    if 'trigger' in option[i]:
                        trigger = option[i]['trigger']
                        if 'has_ethic' in trigger:
                            if type(trigger['has_ethic']) == str:
                                option[i]['zhcn_name'] = '[[File:' + trigger['has_ethic'].replace('"', '') \
                                                         + '.png|16px|link=]]' + option[i]['zhcn_name']
                                option[i]['en_name'] = '[[File:' + trigger['has_ethic'].replace('"', '') + \
                                                       '.png|16px|link=]]' + option[i]['en_name']
                                Danteng.log('Cace 1 :' + trigger['has_ethic'])
                            else:
                                ethic_icon = ''
                                for j in range(len(trigger['has_ethic'])):
                                    ethic_icon = ethic_icon + '[[File:' + trigger['has_ethic'][j].replace('"', '') + \
                                                 '.png|16px|link=]]'
                                option[i]['zhcn_name'] = ethic_icon + option[i]['zhcn_name']
                                option[i]['en_name'] = ethic_icon + option[i]['en_name']
                                Danteng.log('Cace 2 :' + ethic_icon)
                        elif 'OR' in trigger and 'has_ethic' in trigger['OR']:
                            ethic_icon = ''
                            for j in range(len(trigger['OR']['has_ethic'])):
                                ethic_icon = ethic_icon + '[[File:' + trigger['OR']['has_ethic'][j].replace('"', '') +\
                                             '.png|16px|link=]]/'
                            ethic_icon = ethic_icon[0:-1]
                            option[i]['zhcn_name'] = ethic_icon + option[i]['zhcn_name']
                            option[i]['en_name'] = ethic_icon + option[i]['en_name']
                            Danteng.log('Cace 3 :' + ethic_icon)
            value['option'] = option
        refined_data[value['id']] = value
    return refined_data


def tradition_cats_refinery(data):
    refined_data = {}
    for tc_name, tc_value in data.items():
        for i in range(len(tc_value['traditions'])):
            refined_data[tc_value['traditions'][i].replace('"', '')] = tc_name
        refined_data[tc_value['adoption_bonus'].replace('"', '')] = tc_name
        refined_data[tc_value['finish_bonus'].replace('"', '')] = tc_name
    return refined_data


def agendas_refinery(data, i18n_zhcn_map, i18n_en_map):
    # refined_data = OrderedDict()
    # refined_data = data
    return data


# 输出xlsx和json
def save_data(item_category, data):
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
    cn_json = json.dumps(data, ensure_ascii=False)
    with open('json\\' + item_category + '.json', 'w', encoding='UTF-8') as f:
        f.write(cn_json)
