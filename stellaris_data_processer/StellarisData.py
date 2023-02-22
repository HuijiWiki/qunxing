import json
import os
import re
from collections import OrderedDict
import time

import requests

from FoolDonkeyAssignment import pdx_resource, pdx_dict_detail, pdx_logic
from ParadoxData import ParadoxData
from danteng import Danteng
from paradox_parser import ParadoxParser


# 基类 ParadoxData
# abstractmethod data_processor(self)
# abstractmethod refinery(self)
# ================ Common ================
# ================ agendas 议程 ================
class Agendas(ParadoxData):
    def __init__(self):
        super().__init__('agendas')

    def data_processor(self):
        self.raw_data = self.common_processor('agendas')
        agenda_data = self.refinery()
        self.save_data(agenda_data)
        return agenda_data

    def refinery(self):
        for agenda_name, agenda_value in self.raw_data.items():
            # localization debug
            if agenda_value['en_name'] == 'agenda_null':
                agenda_value['zhcn_name'] = '没有议程'
                agenda_value['en_name'] = 'No agenda'
            agenda_value['weight_modifier_logic'] = re.sub(
                r'来自<div style="margin-left:14px">▲(.*?)</div>',
                r'帝国\1', agenda_value['weight_modifier_logic'])
        return self.raw_data


# ================ armies 陆军 ================
class Armies(ParadoxData):
    def __init__(self):
        super().__init__('armies')

    def data_processor(self):
        self.raw_data = self.common_processor('armies')
        armies_data = self.refinery()
        self.save_data(armies_data)
        return armies_data

    def refinery(self):
        data = self.raw_data
        for armies_name, armies_value in data.items():
            if ('cost' in armies_value and len(armies_value['cost']) > 0) or 'time' in armies_value:
                armies_value['zhcn_cost'] = '§E花费：§!'
                if 'cost' in armies_value:
                    for item in armies_value['cost']:
                        if item in pdx_resource:
                            armies_value['zhcn_cost'] += '£' + pdx_resource[item] + armies_value['cost'][
                                item]
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
            self.logic_it('on_queued', armies_value)
            self.logic_it('on_unqueued', armies_value)
            armies_value['potential_logic'] = re.sub(r'来自', r'目标物种', armies_value['potential_logic'])
        return data


# ================ ascension_perks 飞升天赋 ================
class AscensionPerks(ParadoxData):
    def __init__(self):
        super().__init__('ascension_perks')

    def data_processor(self):
        self.raw_data = self.common_processor('ascension_perks')
        ascension_perks_data = self.refinery()
        self.save_data(ascension_perks_data)
        return ascension_perks_data

    def refinery(self):
        data = self.raw_data
        for ap_name, ap_value in data.items():
            if 'on_enabled' in ap_value:
                if 'custom_tooltip' in ap_value['on_enabled']:
                    if type(ap_value['on_enabled']['custom_tooltip']) == str:
                        temp_str = ap_value['on_enabled']['custom_tooltip']
                        ap_value['on_enabled']['custom_tooltip'] = [temp_str]
                    for i in range(len(ap_value['on_enabled']['custom_tooltip'])):
                        if 'custom_tooltip' in ap_value['on_enabled']:
                            tooltip = ap_value['on_enabled']['custom_tooltip'][i].replace('"', '')
                            temp = self.zhcn(tooltip)[0]
                            if 'zhcn_modifier' in ap_value:
                                if ap_value['zhcn_modifier'][-2:] == '\\n':
                                    ap_value['zhcn_modifier'] = ap_value['zhcn_modifier'][0:-2]
                                ap_value['zhcn_modifier'] += '\\n' + temp
                            else:
                                ap_value['zhcn_modifier'] = temp
            if 'ap_galactic_wonders' in ap_name:
                ap_value['icon'] = 'ap_galactic_wonders'
        return data


# ================ bombardment_stances 轨道轰炸姿态 ================
class BombardmentStances(ParadoxData):
    def __init__(self):
        super().__init__('bombardment_stances')

    def data_processor(self):
        self.raw_data = self.common_processor('bombardment_stances')
        bombardment_stances_data = self.refinery()
        self.save_data(bombardment_stances_data)
        return bombardment_stances_data

    def refinery(self):
        data = self.raw_data
        for bs_name, bs_value in data.items():
            self.logic_it('trigger', bs_value)
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
            bs_value['zhcn_name'], bs_value['en_name'] = self.zhcn(name)
            bs_value['zhcn_desc'], bs_value['en_desc'] = self.zhcn(name + '_desc', True)
        return data


# ================ buildings建筑 ================
class Buildings(ParadoxData):
    def __init__(self):
        super().__init__('buildings')

    def data_processor(self):
        self.raw_data = self.common_processor('buildings')
        buildings_data = self.refinery()
        self.save_data(buildings_data)
        return buildings_data

    def refinery(self):
        data = self.raw_data
        for building_name, building_value in data.items():
            Danteng.log(building_name)
            self.logic_it('triggered_planet_modifier', building_value)
            self.logic_it('triggered_desc', building_value)
            self.logic_it('ai_resource_production', building_value)
            self.logic_it('on_queued', building_value)
            self.logic_it('on_unqueued', building_value)
            self.logic_it('on_built', building_value)
            self.logic_it('on_destroy', building_value)
            if 'upgrades' in building_value:
                for i in range(len(building_value['upgrades'])):
                    building_value['upgrades'][i] = building_value['upgrades'][i].replace('"', '')
            # for item in icon_dict:
            #     if item in building_value:
            #         temp_str = ''
            #         for res in building_value[item]:
            #             if res in fool_donkey_dict_resource:
            #                 res_icon = '£' + fool_donkey_dict_resource[res]
            #             else:
            #                 res_icon = '£' + res
            #             temp_str += res_icon + ' ' + building_value[item][res] + ' '
            #         building_value[item + '_string'] = temp_str
            # if 'produced_resource_trigger' in building_value:
            #     self.logic_it('produced_resource_trigger', building_value)
            #     for icon_item in fool_donkey_dict_resource:
            #         building_value['produced_resource_trigger_logic'] = \
            #             re.sub(icon_item + r':\s*(\d*)', '£' + fool_donkey_dict_resource[icon_item] + r'\1',
            #                    building_value['produced_resource_trigger_logic'])
            # if 'adjacency_bonus' in building_value:
            #     bonus_str = ''
            #     for bonus_item in building_value['adjacency_bonus']:
            #         bonus_str += self.zhcn(bonus_item)[0] + ':§G+' + \
            #                      building_value['adjacency_bonus'][bonus_item] + '§!\\n'
            #     building_value['adjacency_bonus_string'] = bonus_str
            #     Danteng.log(building_value['adjacency_bonus_string'])
        return data


# ================ casus_belli宣战借口 ================
class CasusBelli(ParadoxData):
    def __init__(self):
        super().__init__('casus_belli')

    def data_processor(self):
        self.raw_data = self.common_processor('casus_belli')
        casus_belli_data = self.refinery()
        self.save_data(casus_belli_data)
        return casus_belli_data

    def refinery(self):
        data = self.raw_data
        for cb_name, cb_value in data.items():
            if 'zhcn_name' in cb_value:
                name = 'casus_belli_' + cb_value['zhcn_name']
                cb_value['zhcn_name'], cb_value['en_name'] = self.zhcn(name)
                desc = name + '_acquire_hint'
                cb_value['zhcn_desc'], cb_value['en_desc'] = self.zhcn(desc, True)
            if 'is_valid' in cb_value:
                self.logic_it('is_valid', cb_value)
                cb_value['is_valid_logic'] = re.sub(r'与§H自己§!相同', r'与§H防御方§!相同', cb_value['is_valid_logic'])
                cb_value['is_valid_logic'] = re.sub(r'与§H自己§!不同', r'与§H防御方§!不同', cb_value['is_valid_logic'])
            cb_value['wargoals'] = []
        for item in self.all_data['war_goals']:
            if 'casus_belli' in item:
                for cb in data:
                    if data[cb]['key'] == item['casus_belli']:
                        data[cb]['war_goals'].append(item['key'])
        return data


# ================ component_sets 组件图标 ================
class ComponentSets(ParadoxData):
    def __init__(self):
        super().__init__('component_sets')

    def data_processor(self):
        self.raw_data = self.common_processor('component_sets')
        component_sets_data = self.refinery()
        self.save_data(component_sets_data)
        return component_sets_data

    def refinery(self):
        refined_data = OrderedDict()
        for cs_name, cs_value in self.raw_data.items():
            name = cs_value['key'].replace('"', '')
            refined_data[name] = {}
            refined_data[name]['key'] = name
            icon = cs_value['icon'].replace('"', '')
            refined_data[name]['icon'] = icon
            if icon in self.icon_dict:
                refined_data[name]['icon'] = self.icon_dict[icon]['icon']
        return refined_data


# ================ component_templates 组件模板 ================
class ComponentTemplates(ParadoxData):
    def __init__(self):
        self.component_add = OrderedDict()
        super().__init__('component_templates')

    def data_processor(self):
        pp = ParadoxParser(os.path.join(self.base_path + 'common\\component_templates\\weapon_components.csv'),
                           self.item_category)
        self.component_add = pp.data
        self.raw_data = self.common_processor('component_templates')
        component_templates_data = self.refinery()
        self.save_data(component_templates_data)
        return component_templates_data

    def refinery(self):
        refined_data = OrderedDict()
        for ct_name, ct_value in self.raw_data.items():
            key = ct_value['key'].replace('"', '')
            ct_value['key'] = key
            ct_value['zhcn_name'], ct_value['en_name'] = self.zhcn(key)
            ct_value['zhcn_desc'], ct_value['en_desc'] = self.zhcn(key + '_DESC', True)
            if 'component_set' in ct_value:
                ct_value['component_set'] = ct_value['component_set'].replace('"', '')

            if 'icon' in ct_value:
                icon = ct_value['icon'].replace('"', '')
                Danteng.log('图标：' + ct_value['icon'])
                if icon in self.icon_dict:
                    ct_value['icon'] = self.icon_dict[icon]['icon']
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
                    ct_value['instruction'][i] = self.zhcn(ct_value['instruction'][i])[0]
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
                        self.zhcn(ct_value['hostile_aura']['name'])
                if 'modifier' in ct_value['hostile_aura']:
                    Danteng.log('\n' + ct_value['hostile_aura']['zhcn_name'] + '的modifier：' + 'modifier')
                    ct_value['hostile_aura']['zhcn_modifier'] = self.modifier_processor(
                        ct_value['hostile_aura']['modifier'])
            if 'friendly_aura' in ct_value:
                # ct_value['icon'] = 'ship_part_aura_nanobot'
                if 'name' in ct_value['friendly_aura']:
                    ct_value['friendly_aura']['name'] = ct_value['friendly_aura']['name'].replace('"', '')
                    ct_value['friendly_aura']['zhcn_name'], ct_value['friendly_aura']['en_name'] = \
                        self.zhcn(ct_value['friendly_aura']['name'])
                if 'modifier' in ct_value['friendly_aura']:
                    Danteng.log('\n' + ct_value['friendly_aura']['zhcn_name'] + '的modifier：' + 'modifier')
                    ct_value['friendly_aura']['zhcn_modifier'] = self.modifier_processor(
                        ct_value['friendly_aura']['modifier'])
            if 'size' in ct_value:
                ct_value['size'] = ct_value['size'].lower()
            if 'component_set' not in ct_value:
                ct_value['component_set'] = ''
            if 'class_restriction' in ct_value:
                ct_value['zhcn_class_restriction'] = ''
                for i in range(len(ct_value['class_restriction'])):
                    ct_value['zhcn_class_restriction'] = ct_value['zhcn_class_restriction'] + \
                                                         self.zhcn(ct_value['class_restriction'][i])[
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
                    ct_value['ai_task'] += self.zhcn(ct_value['ai_tags'][i])[0] + ','
                ct_value['ai_task'] = ct_value['ai_task'][0:-1]
            if 'instruction' in ct_value:
                ct_value['zhcn_instruction'] = ''
                for i in range(len(ct_value['instruction'])):
                    ct_value['zhcn_instruction'] += self.zhcn(ct_value['instruction'][i])[0] + ','
                ct_value['zhcn_instruction'] = ct_value['zhcn_instruction'][0:-1]
            if 'component_set' in ct_value:
                ct_value['sets'] = self.zhcn(ct_value['component_set'])[0]
            if ct_value['key'] in self.component_add:
                ct_value.update(self.component_add[ct_value['key']])
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


# ================ decisions 行星决议 ================
class Decisions(ParadoxData):
    def __init__(self):
        super().__init__('decisions')

    def data_processor(self):
        self.raw_data = self.common_processor('decisions')
        deposits_data = self.refinery()
        self.save_data(deposits_data)
        return deposits_data

    def refinery(self):
        data = self.raw_data
        non_image = []
        for name, value in data.items():
            if 'effect' in value:
                if 'add_modifier' in value['effect'] and 'modifier' in value['effect']['add_modifier']:
                    value['effect']['add_modifier']['modifier'] = \
                        value['effect']['add_modifier']['modifier'].replace('"', '')
                if 'custom_tooltip' in value['effect']:
                    more_desc = self.zhcn(value['effect']['custom_tooltip'].replace('"', ''))
                    value['zhcn_desc'] += more_desc[0]
                    value['en_desc'] += more_desc[1]
                if 'IF' in value['effect']:
                    self.logic_it('IF', value['effect'])
                if 'hidden_effect' in value['effect']:
                    if 'add_modifier' in value['effect']['hidden_effect'] and \
                            'modifier' in value['effect']['hidden_effect']['add_modifier']:
                        value['effect']['hidden_effect']['add_modifier']['modifier'] = \
                            value['effect']['hidden_effect']['add_modifier']['modifier'].replace('"', '')
                    if type(value['effect']['hidden_effect']) == list:
                        temp = OrderedDict()
                        for i in range(len(value['effect']['hidden_effect'])):
                            temp.update(value['effect']['hidden_effect'][i])
                        value['effect']['hidden_effect'] = temp
            base_image_path = r'F:\TEMP\gfx\interface\icons\decisions'
            icon_name = ''
            if 'icon' in value:
                icon_name = value['icon']
            else:
                icon_name = name
            if not os.path.exists(os.path.join(base_image_path, icon_name + '.png')):
                value['icon'] = 'default_decision'
                non_image.append(os.path.join(base_image_path, icon_name + '.png'))
        return data


# ================ deposits 矿脉 ================
class Deposits(ParadoxData):
    def __init__(self):
        super().__init__('deposits')

    def data_processor(self):
        self.raw_data = self.common_processor('deposits')
        deposits_data = self.refinery()
        self.save_data(deposits_data)
        return deposits_data

    def refinery(self):
        data = self.raw_data
        temp = []
        for deposit_name, deposit_value in data.items():
            if deposit_name == 'd_null_deposit':
                deposit_value['icon'] = 'default_deposit'
                deposit_value['zhcn_name'] = '空矿脉'
                deposit_value['en_name'] = 'null deposit'
            elif deposit_name == 'd_natural_farmland':
                deposit_value['icon'] = 'd_bountiful_plains'
            elif deposit_name == 'd_mineral_striations':
                deposit_value['icon'] = 'd_prosperous_mesa'
            elif deposit_name == 'd_buzzing_plains':
                deposit_value['icon'] = 'd_fertile_lands'
            if deposit_value['zhcn_name'] == deposit_value['en_name'] and '£' not in deposit_value['zhcn_name']:
                if 'produces_detail' in deposit_value:
                    deposit_value['zhcn_name'] = deposit_value['produces_detail']
                    deposit_value['en_name'] = deposit_value['produces_detail']
            if 'category' in deposit_value:
                cat = self.all_data['deposit_categories'][deposit_value['category']]
                if 'blocker' in cat:
                    deposit_value['blocker'] = cat['blocker']
                if 'important' in cat:
                    deposit_value['important'] = cat['important']
            self.logic_it('on_cleared', deposit_value)
            self.logic_it('can_be_cleared', deposit_value)
            self.logic_it('triggered_planet_modifier', deposit_value)
            if 'station' in deposit_value:
                deposit_value['icon'] = 'default_deposit'
            if 'on_cleared' in deposit_value and 'blocker_swap_types' in deposit_value:
                temp.append(deposit_value)
        return data


# ================ deposit_categories 矿脉类型 ================
class DepositCategories(ParadoxData):
    def __init__(self):
        super().__init__('deposit_categories')

    def data_processor(self):
        self.raw_data = self.common_processor('deposit_categories')
        deposit_categories_data = self.refinery()
        self.save_data(deposit_categories_data)
        return deposit_categories_data

    def refinery(self):
        data = self.raw_data
        return data


# ================ districts 区划 ================
class Districts(ParadoxData):
    def __init__(self):
        super().__init__('districts')

    def data_processor(self):
        self.raw_data = self.common_processor('districts')
        districts_data = self.refinery()
        self.save_data(districts_data)
        return districts_data

    def refinery(self):
        data = self.raw_data
        for name, value in data.items():
            self.logic_it('show_on_uncolonized', value)
            self.logic_it('triggered_planet_modifier', value)
            if 'triggered_desc' in value:
                triggered_desc = self.zhcn(value['triggered_desc'])
                value['zhcn_desc'] += '\n' + triggered_desc[0]
                value['en_desc'] += '\n' + triggered_desc[1]
            self.logic_it('ai_resource_production', value)
        return data


# ================ edicts 法令 ================
class Edicts(ParadoxData):
    def __init__(self):
        super().__init__('edicts')

    def data_processor(self):
        self.raw_data = self.common_processor('edicts')
        edicts_data = self.refinery()
        self.save_data(edicts_data)
        return edicts_data

    def refinery(self):
        data = self.raw_data
        for edicts_name, edicts_value in data.items():
            if edicts_value['zhcn_name'] == edicts_value['key']:
                edicts_value['zhcn_name'], edicts_value['en_name'] = self.zhcn('edict_' + edicts_value['key'])
            if 'cost' in edicts_value and len(edicts_value['cost']) > 0:
                edicts_value['zhcn_cost'] = '§E基础花费：§!'
                for item in edicts_value['cost']:
                    if item in pdx_resource:
                        edicts_value['zhcn_cost'] += '£' + pdx_resource[item] + edicts_value['cost'][item]
            if 'effect' in edicts_value and len(edicts_value['effect']) > 0:
                if 'custom_tooltip' in edicts_value['effect']:
                    edicts_value['zhcn_modifier'] = self.zhcn(edicts_value['effect']['custom_tooltip'])[0]
                elif 'if' in edicts_value['effect']:
                    edicts_value['zhcn_modifier'] = self.choice(edicts_value['effect'], 1)[2:]
            if 'resources' in edicts_value and 'category' in edicts_value['resources']:
                edicts_value['category'] = edicts_value['resources']['category']
        return data


# ================ ethics 思潮 ================
class Ethics(ParadoxData):
    def __init__(self):
        super().__init__('ethics')

    def data_processor(self):
        self.raw_data = self.common_processor('ethics')
        ethic_data = self.refinery()
        self.save_data(ethic_data)
        return ethic_data

    def refinery(self):
        refined_data = OrderedDict()
        for ethic_name, ethics_value in self.raw_data.items():
            if ethic_name != 'ethic_categories':
                self.logic_it('pop_attraction_tag', ethics_value)
                self.logic_it('pop_attraction', ethics_value)
                refined_data[ethic_name] = ethics_value
        return refined_data


# ================ global_ship_designs 预置舰船设计 ================
class GlobalShipDesigns(ParadoxData):
    def __init__(self):
        super().__init__('global_ship_designs')

    def data_processor(self):
        self.raw_data = self.common_processor('global_ship_designs')
        design_data = self.refinery()
        self.save_data(design_data)
        return design_data

    def refinery(self):
        refined_data = OrderedDict()
        for design_name, design_value in self.raw_data.items():
            name = re.sub(r'^global_ship_design_', r'', design_name)
            design_value['key'] = name
            design_value['zhcn_name'], design_value['en_name'] = self.zhcn(name)
            design_value['name'] = name
            Danteng.log(name)
            if 'section' in design_value and type(design_value['section']) != list:
                design_value['section'] = [design_value['section']]
            if 'required_component' in design_value:
                if type(design_value['required_component']) != list:
                    design_value['required_component'] = [design_value['required_component']]
                for i in range(len(design_value['required_component'])):
                    design_value['required_component'][i] = design_value['required_component'][i].replace('"', '')
            if 'section' not in design_value:
                continue
            for i in range(len(design_value['section'])):
                section = design_value['section'][i]
                section['template'] = section['template'].replace('"', '')
                section['slot'] = section['slot'].replace('"', '')
                component = OrderedDict()

                if 'component' not in section:
                    continue
                if type(section['component']) != list:
                    section['component'] = [section['component']]
                for j in range(len(section['component'])):
                    slot = section['component'][j]
                    if 'template' in slot:
                        component[slot['slot'].replace('"', '')] = slot['template'].replace('"', '')
                    else:
                        component[slot['slot'].replace('"', '')] = {}
                        z = 2
                section['component'] = component
            refined_data[name] = design_value
        return refined_data


# ================ governments 政府 ================
class Governments(ParadoxData):
    def __init__(self):
        super().__init__('governments')

    def data_processor(self):
        self.raw_data = self.common_processor('governments')
        governments_data = self.refinery()
        self.save_data(governments_data)
        return governments_data

    def refinery(self):
        data = self.raw_data
        title = ['ruler_title', 'ruler_title_female', 'heir_title', 'heir_title_female', 'leader_class']
        for gov_name, gov_value in data.items():
            for item in title:
                if item in gov_value:
                    gov_value[item + '_desc'] = self.zhcn(gov_value[item])[0]
                    Danteng.log(gov_value[item + '_desc'])
        return data


# ================ authorities 权利制度 ================
class Authorities(ParadoxData):
    def __init__(self):
        super().__init__('authorities')

    def data_processor(self):
        self.raw_data = self.common_processor('governments\\authorities')
        authorities_data = self.refinery()
        self.save_data(authorities_data)
        return authorities_data

    def refinery(self):
        data = self.raw_data
        for name, value in data.items():
            value['desc_detail'] = ''
            value['desc_detail'] = self.authorities_detail_processor(value)
        return data

    def authorities_detail_processor(self, value):
        detail_str = ''
        for item in pdx_dict_detail:
            if item in value:
                if value[item] == 'no':
                    detail_str += '△' + pdx_dict_detail[item]['deny'] + pdx_dict_detail[item][
                        'value'] + '\\n'
                elif value[item] == 'yes':
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + '\\n'
                elif value[item] in self.i18n_zhcn_map:
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + self.i18n_zhcn_map[
                        value[item]] + '\\n'
                elif ('auth_' + value[item]) in self.i18n_zhcn_map:
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + self.i18n_zhcn_map[
                        'auth_' + value[item]] + '\\n'
                elif value[item] in self.i18n_en_map:
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + self.i18n_en_map[
                        value[item]] + '\\n'
                elif ('auth_' + value[item]) in self.i18n_en_map:
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + self.i18n_en_map[
                        'auth_' + value[item]] + '\\n'
                else:
                    detail_str += '▲' + pdx_dict_detail[item]['value'] + value[item] + '\\n'
        Danteng.log(detail_str)
        return detail_str


# ================ Civics 国家理念 ================
class Civics(ParadoxData):
    def __init__(self):
        super().__init__('civics')

    def data_processor(self):
        self.raw_data = self.common_processor('governments\\civics')
        civics_data = self.refinery()
        self.save_data(civics_data)
        return civics_data

    def refinery(self):
        data = self.raw_data
        for civic_name, civic_value in data.items():
            if 'description' in civic_value:
                desc = civic_value['description'].replace('"', '')
                civic_value['zhcn_modifier'] = self.zhcn(desc)[0]
                find = re.findall(r'\$.*?\$', civic_value['zhcn_modifier'])
                if find:
                    for item in find:
                        find_key = item[1:-1]
                        if find_key in self.i18n_zhcn_map:
                            civic_value['zhcn_modifier'] = civic_value['zhcn_modifier'] \
                                .replace(item, self.i18n_zhcn_map[find_key])
                            Danteng.log(civic_name)
                            # civic_value['en_modifier'] = civic_value['en_modifier'] \
                            #     .replace(item, self.i18n_en_map[find_key])
                        elif find_key in self.i18n_en_map:
                            civic_value['zhcn_modifier'] = civic_value['zhcn_modifier'] \
                                .replace(item, self.i18n_en_map[find_key])
                            # civic_value['en_modifier'] = civic_value['en_modifier'] \
                            #     .replace(item, self.i18n_en_map[find_key])
            if 'zhcn_modifier' in civic_value:
                Danteng.log(civic_value['zhcn_modifier'])
            if 'random_weight_logic' in civic_value:
                if civic_value['random_weight_logic'].find('game_started') != -1:
                    civic_value['moddable'] = 'false'
                else:
                    civic_value['moddable'] = 'true'
            if 'has_secondary_species' in civic_value:
                if 'traits' in civic_value['has_secondary_species']:
                    civic_value['secondary_trait'] = civic_value['has_secondary_species']['traits']['trait']
                civic_value['secondary_zhcn_desc'], civic_value['secondary_en_desc'] = \
                    self.zhcn(civic_value['has_secondary_species']['title'])
            # if 'playable' in civic_value:
            #     if 'NOT' in civic_value['playable']:
            #         civic_value['potential_logic'] += self.indentation + "△没有§H" + fool_donkey_logic[
            #             civic_value['playable']['NOT']['host_has_dlc'].replace('"', '')]['value'] + "§!DLC" + '</div>'
            #     else:
            #         civic_value['potential_logic'] += self.indentation + "▲拥有§H" + fool_donkey_logic[
            #             civic_value['playable']['host_has_dlc'].replace('"', '')]['value'] + "§!DLC" + '</div>'
            # if 'potential_logic' in civic_value:
            #     if civic_value['potential_logic'].find('国家类型是§H') != -1:
            #         civic_value['icon'] = 'civic_agrarian_idyll'
        return data


# ================ megastructures 巨构建筑 ================
class Megastructures(ParadoxData):
    def __init__(self):
        super().__init__('megastructures')

    def data_processor(self):
        self.raw_data = self.common_processor('megastructures')
        megastructures_data = self.refinery()
        self.save_data(megastructures_data)
        return megastructures_data

    def refinery(self):
        data = self.raw_data
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
            self.logic_it('placement_rules', ms_value)
            self.logic_it('on_build_start', ms_value)
            self.logic_it('on_build_cancel', ms_value)
            self.logic_it('on_build_complete', ms_value)
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
            elif ms_name[0:19] == 'matter_decompressor':
                ms_value['icon'] = 'tech_matter_decompressor'
                ms_value['type'] = 'matter_decompressor'
            elif ms_name[0:29] == 'strategic_coordination_center':
                ms_value['icon'] = 'tech_strategic_coordination_center'
                ms_value['type'] = 'strategic_coordination_center'
            elif ms_name[0:21] == 'mega_art_installation':
                ms_value['icon'] = 'tech_mega_art_installation'
                ms_value['type'] = 'mega_art_installation'
            elif ms_name[0:21] == 'interstellar_assembly':
                ms_value['icon'] = 'tech_interstellar_assembly'
                ms_value['type'] = 'interstellar_assembly'
            elif ms_name[0:5] == 'lgate':
                ms_value['icon'] = 'tech_lgate_activation'
                ms_value['type'] = 'lgate'
            if ms_name + '_megastructure_details' in self.i18n_zhcn_map:
                ms_value['megastructure_details'] = self.i18n_zhcn_map[ms_name + '_megastructure_details']
            if ms_name + '_construction_info_delayed' in self.i18n_zhcn_map:
                ms_value['construction_info_delayed'] = self.i18n_zhcn_map[ms_name + '_construction_info_delayed']
        return data


# ================ personalities AI性格 ================
class Personalities(ParadoxData):
    def __init__(self):
        super().__init__('personalities')

    def data_processor(self):
        self.raw_data = self.common_processor('personalities')
        personalities_data = self.refinery()
        self.save_data(personalities_data)
        return personalities_data

    def refinery(self):
        data = self.raw_data
        for p_name, p_value in data.items():
            name = 'personality_' + p_value['key']
            desc = name + '_desc'
            p_value['zhcn_name'], p_value['en_name'] = self.zhcn(name)
            p_value['zhcn_desc'], p_value['en_desc'] = self.zhcn(desc, True)
            if 'behaviour' in p_value:
                p_value['zhcn_behaviour'] = '§E行为模式：§!\\n'
                for name, value in p_value['behaviour'].items():
                    string = 'personality_type_' + name
                    p_value['zhcn_behaviour'] += self.zhcn(string)[0] + '：'
                    if value == 'yes':
                        p_value['zhcn_behaviour'] += '§H是§!\\n'
                    else:
                        p_value['zhcn_behaviour'] += '§H否§!\\n'
            if 'weapon_preferences' in p_value:
                p_value['zhcn_weapon'] = self.zhcn(p_value['weapon_preferences'])[0]
        return data


# ================ planet_classes 行星类型 ================
class PlanetClasses(ParadoxData):
    def __init__(self):
        super().__init__('planet_classes')

    def data_processor(self):
        self.raw_data = self.common_processor('planet_classes')
        planet_classes_data = self.refinery()
        self.save_data(planet_classes_data)
        return planet_classes_data

    def refinery(self):
        refined_data = OrderedDict()
        for pc_name, pc_value in self.raw_data.items():
            if pc_name[0:3] == 'pc_':
                if 'climate' in pc_value:
                    climate = pc_value['climate'][1:-1]
                    pc_value['climate_desc'] = self.zhcn(climate)[0]
                pc_value['desc_detail'] = '模型大小：' + pc_value['entity_scale'] + '\\n' + '星球大小：'
                if 'max' in pc_value['planet_size'] and 'min' in pc_value['planet_size']:
                    pc_value['desc_detail'] += pc_value['planet_size']['min'] + '~' + pc_value['planet_size']['max'] \
                                               + '\\n'
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
                                        self.zhcn('gray_goo_world_inactive_nanites')[0] + \
                                        '\\n§H拥有全局变量§Yactive_gray_goo§!时的描述：§!\\n' + \
                                        self.zhcn('gray_goo_world_active_nanites')[0]
        return refined_data


# ================ planet_modifiers 行星修正 ================
class PlanetModifiers(ParadoxData):
    def __init__(self):
        super().__init__('planet_modifiers')

    def data_processor(self):
        self.raw_data = self.common_processor('planet_modifiers')
        planet_modifiers_data = self.refinery()
        self.save_data(planet_modifiers_data)
        return planet_modifiers_data

    def refinery(self):
        data = self.raw_data
        static_modifiers = self.all_data['static_modifiers']
        for pc_name, pc_value in data.items():
            if 'zhcn_modifier' in pc_value:
                pc_value['zhcn_name'] = pc_value['zhcn_modifier']
            # localization debug
            if pc_value['en_name'] == 'pm_null':
                pc_value['zhcn_name'] = '无修正'
                pc_value['en_name'] = 'No Modifier'
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
                self.logic_it('spawn_chance', pc_value)
            else:
                pc_value['spawn_chance_logic'] = '无'
        return data


# ================ policies 政策 ================
class Policies(ParadoxData):
    def __init__(self):
        super().__init__('policies')

    def data_processor(self):
        self.raw_data = self.common_processor('policies')
        policies_data = self.refinery()
        self.save_data(policies_data)
        return policies_data

    def refinery(self):
        data = self.raw_data
        option_keys = []
        for policies_name, policies_value in data.items():
            name = 'policy_' + policies_value['key']
            policies_value['zhcn_name'], policies_value['en_name'] = self.zhcn(name)
            policies_value['zhcn_desc'], policies_value['en_desc'] = self.zhcn(name + '_desc', True)
            if 'option' in policies_value:
                for options in policies_value['option']:
                    name = options['name'].replace('"', '')
                    desc = options['name'].replace('"', '') + '_desc'
                    options['zhcn_name'], options['en_name'] = self.zhcn(name)
                    options['zhcn_desc'], options['en_desc'] = self.zhcn(desc, True)
                    self.logic_it('valid', options)
                    self.logic_it('AI_weight', options)
                    self.logic_it('on_enabled', options)
                    self.logic_it('on_disabled', options)
                    self.logic_it('potential', options)
                    if 'modifier' in options:
                        if len(options['modifier']) == 0:
                            options.pop('modifier')
                        else:
                            Danteng.log('\n选项：' + options['zhcn_name'] + '的modifier：' + 'modifier')
                            options['zhcn_modifier'] = self.modifier_processor(options['modifier'])
                    for op_name in options:
                        if op_name not in option_keys:
                            option_keys.append(op_name)  # 统计字段用
        return data


# ================ pop_categories 人口分类 ================
class PopCategories(ParadoxData):
    def __init__(self):
        super().__init__('pop_categories')

    def data_processor(self):
        self.raw_data = self.common_processor('pop_categories')
        pop_categories_data = self.refinery()
        self.save_data(pop_categories_data)
        return pop_categories_data

    def refinery(self):
        data = self.raw_data
        for name, value in data.items():
            self.logic_it('should_apply_unemployment_penalties', value)
            if 'unemployment_penalties' in value:
                value['zhcn_unemployment_penalties'] = self.modifier_processor(value['unemployment_penalties'])
            self.logic_it('unemployment_resources', value)
            self.logic_it('triggered_planet_modifier', value)
            self.logic_it('assign_to_pop', value)
            if 'resettlement_cost' in value:
                value['resettlement_detail'] = ''
                for res, cost_value in value['resettlement_cost'].items():
                    value['resettlement_detail'] += '£' + res + cost_value
        return data


# ================ pop_faction_types 派系 ================
class PopFactionTypes(ParadoxData):
    def __init__(self):
        super().__init__('pop_faction_types')

    def data_processor(self):
        self.raw_data = self.common_processor('pop_faction_types')
        pft_data = self.refinery()
        self.save_data(pft_data)
        return pft_data

    def refinery(self):
        data = self.raw_data
        demand_keys = []
        for pft_name, pft_value in data.items():
            name = 'pft_' + pft_value['key']
            desc = 'pft_' + pft_value['key'] + '_desc'
            pft_value['zhcn_name'], pft_value['en_name'] = self.zhcn(name)
            pft_value['zhcn_desc'], pft_value['en_desc'] = self.zhcn(desc, True)
            if 'election_header' in pft_value:
                pft_value['election_header'] = pft_value['election_header'].replace('"', '')
            self.logic_it('is_potential', pft_value)
            # self.logic_it('parameters', pft_value)
            self.logic_it('can_join_faction', pft_value)
            self.logic_it('attraction', pft_value)
            self.logic_it('leader', pft_value)
            if 'demand' in pft_value:
                for i in range(len(pft_value['demand'])):
                    pft_value['demand'][i]['title'] = pft_value['demand'][i]['title'].replace('"', '')
                    pft_value['demand'][i]['unfulfilled_title'] = pft_value['demand'][i]['unfulfilled_title'] \
                        .replace('"', '')
                    pft_value['demand'][i]['desc'] = pft_value['demand'][i]['desc'].replace('"', '')
                    pft_value['demand'][i]['zhcn_name'] = self.zhcn(pft_value['demand'][i]['title'])[0]
                    pft_value['demand'][i]['un_name'] = self.zhcn(pft_value['demand'][i]['unfulfilled_title'])[0]
                    pft_value['demand'][i]['zhcn_name'] = self.zhcn(pft_value['demand'][i]['zhcn_name'])[0] \
                        .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                        .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                        .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                        .replace('[Root.Owner.GetAdj]', '帝国') \
                        .replace('[Root.Owner.GetName]', '帝国') \
                        .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')
                    pft_value['demand'][i]['un_name'] = self.zhcn(pft_value['demand'][i]['un_name'])[0] \
                        .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                        .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                        .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                        .replace('[Root.Owner.GetAdj]', '帝国') \
                        .replace('[Root.Owner.GetName]', '帝国') \
                        .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')
                    pft_value['demand'][i]['desc'] = self.zhcn(pft_value['demand'][i]['desc'])[0] \
                        .replace('[Root.GetName]', '§H' + pft_value['zhcn_name'] + '§!') \
                        .replace('[Root.Owner.GetSpeciesName]', '主体种族') \
                        .replace('[Root.Owner.GetRulerTitle]', '统治者') \
                        .replace('[Root.Owner.GetAdj]', '帝国') \
                        .replace('[Root.Owner.GetName]', '帝国') \
                        .replace('[Root.Owner.GetSpeciesNamePlural]', '主体')

                    self.logic_it('potential', pft_value['demand'][i])
                    self.logic_it('trigger', pft_value['demand'][i])
                    for key_name in pft_value['demand'][i]:
                        if key_name not in demand_keys:
                            demand_keys.append(key_name)
            self.logic_it('on_create', pft_value)
            self.logic_it('on_destroy', pft_value)
            if 'actions' in pft_value:
                for item in pft_value['actions']:
                    pft_value['actions'][item]['zhcn_name'] = self.zhcn(pft_value['actions'][item]['title'].
                                                                        replace('"', ''), )[0]
                    if 'cost' in pft_value['actions'][item]:
                        pft_value['actions'][item]['zhcn_cost'] = ''
                        for cost in pft_value['actions'][item]['cost']:
                            if cost in pdx_resource:
                                pft_value['actions'][item]['zhcn_cost'] += '£' + pdx_resource[cost] + \
                                                                           pft_value['actions'][item]['cost'][cost]
                    self.logic_it('potential', pft_value['actions'][item])
                    self.logic_it('valid', pft_value['actions'][item])
                    self.logic_it('effect', pft_value['actions'][item])
                    self.logic_it('ai_weight', pft_value['actions'][item])
        return data


# ================ pop_jobs 职业 ================
class PopJobs(ParadoxData):
    def __init__(self):
        super().__init__('pop_jobs')

    def data_processor(self):
        self.raw_data = self.common_processor('pop_jobs')
        jobs_data = self.refinery()
        self.save_data(jobs_data)
        return jobs_data

    def refinery(self):
        data = self.raw_data
        count_cat = []
        for name, value in data.items():
            if 'icon' in value:
                value['icon'] = 'job_' + value['icon']
            if 'zhcn_condition_string' in value:
                value['zhcn_condition_string'], value['en_condition_string'] = self.zhcn(value['condition_string'],
                                                                                         True)
            if 'category' in value:
                if value['category'] not in count_cat:
                    count_cat.append(value['category'])
            self.logic_it('triggered_country_modifier', value)
            self.logic_it('triggered_planet_modifier', value)
            self.logic_it('triggered_pop_modifier', value)
        return data


# ================ relics 遗珍 ================
class Relics(ParadoxData):
    def __init__(self):
        super().__init__('relics')

    def data_processor(self):
        self.raw_data = self.common_processor('relics')
        relics_data = self.refinery()
        self.save_data(relics_data)
        return relics_data

    def refinery(self):
        data = self.raw_data
        for name, value in data.items():
            value['portrait'] = value['portrait'].replace('"', '')
            if value['portrait'] in self.icon_dict:
                value['icon'] = self.icon_dict[value['portrait']]['icon']
            self.logic_it('triggered_country_modifier', value)
            self.logic_it('active_effect', value)
            # self.logic_it('possible', value)
        return data


# ================ section_templates 区块 ================
class SectionTemplates(ParadoxData):
    def __init__(self):
        super().__init__('section_templates')

    def data_processor(self):
        self.raw_data = self.common_processor('section_templates')
        section_templates_data = self.refinery()
        self.save_data(section_templates_data)
        return section_templates_data

    def refinery(self):
        refined_data = OrderedDict()
        for st_name, st_value in self.raw_data.items():
            st_value['key'] = st_value['key'].replace('"', '')
            st_value['zhcn_name'], st_value['en_name'] = self.zhcn(st_value['key'], True)
            refined_data[st_value['key']] = st_value
            # if 'ship_size' in st_value:
            #     if type(st_value['ship_size']) == str:
            #         st_value['ship_size'] = [st_value['ship_size']]
            #     st_value['zhcn_ship_size'] = '§E适用舰船类型：§!'
            #     for i in range(len(st_value['ship_size'])):
            #         st_value['zhcn_ship_size'] += self.zhcn(st_value['ship_size'][i], True)[0] + '，'
            #     st_value['zhcn_ship_size'] = st_value['zhcn_ship_size'][0:-1]
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
                    if 'slot_type' in st_value['component_slot'][i]:
                        if st_value['component_slot'][i]['slot_type'] == 'weapon':
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
                            elif st_value['component_slot'][i]['slot_size'] == 'extra_large':
                                st_value['slot_count']['X'] += 1
                            elif st_value['component_slot'][i]['slot_size'] == 'titanic':
                                st_value['slot_count']['T'] += 1
                            elif st_value['component_slot'][i]['slot_size'] == 'planet_killer':
                                st_value['slot_count']['W'] += 1
                        elif st_value['component_slot'][i]['slot_type'] == 'strike_craft':
                            st_value['slot_count']['H'] += 1
                    for cs_name, cs_value in st_value['component_slot'][i].items():
                        Danteng.log(st_name + ' component_slot ' + cs_name + ': ')
                        if type(st_value['component_slot'][i][cs_name]) == str:
                            st_value['component_slot'][i][cs_name] = cs_value.replace('"', '')
            if 'small_utility_slots' in st_value:
                st_value['small_utility_slots'] = int(st_value['small_utility_slots'])
            if 'medium_utility_slots' in st_value:
                st_value['medium_utility_slots'] = int(st_value['medium_utility_slots'])
            if 'large_utility_slots' in st_value:
                st_value['large_utility_slots'] = int(st_value['large_utility_slots'])
        return refined_data


# ================ ship_behaviors 舰船行为 ================
class ShipBehaviors(ParadoxData):
    def __init__(self):
        super().__init__('ship_behaviors')

    def data_processor(self):
        self.raw_data = self.common_processor('ship_behaviors')
        ship_behaviors_data = self.refinery()
        self.save_data(ship_behaviors_data)
        return ship_behaviors_data

    def refinery(self):
        refined_data = OrderedDict()
        for sb_name, sb_value in self.raw_data.items():
            key = sb_value['key'].replace('"', '')
            sb_value['key'] = key
            if 'desc' in sb_value:
                desc = sb_value['desc'].replace('"', '')
                sb_value['zhcn_desc'], sb_value['en_desc'] = self.zhcn(desc, True)
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


# ================ ship_sizes 舰船类型 ================
class ShipSizes(ParadoxData):
    def __init__(self):
        super().__init__('ship_sizes')

    def data_processor(self):
        self.raw_data = self.common_processor('ship_sizes')
        ship_sizes_data = self.refinery()
        self.save_data(ship_sizes_data)
        return ship_sizes_data

    def refinery(self):
        data = self.raw_data
        for ss_name, ss_value in data.items():
            if 'graphical_culture' in ss_value:
                find = re.findall(r'\"(.*?)\"', ss_value['graphical_culture'][0])
                if find:
                    ss_value['graphical_culture'] = find
            if 'pre_communications_name' in ss_value:
                ss_value['pre_communications_name'] = self.zhcn(ss_value['pre_communications_name'].replace('"', ''))[0]
            if 'class' in ss_value:
                ss_value['zhcn_class'] = self.zhcn(ss_value['class'])[0]
            if 'construction_type' in ss_value:
                ss_value['zhcn_construction_type'] = self.zhcn(ss_value['construction_type'])[0]
            if 'required_component_set' in ss_value:
                ss_value['zhcn_required_component_set'] = '§E需要组件：§!'
                if type(ss_value['required_component_set']) == str:
                    ss_value['required_component_set'] = [ss_value['required_component_set']]
                for i in range(len(ss_value['required_component_set'])):
                    ss_value['required_component_set'][i] = ss_value['required_component_set'][i].replace('"', '')
                    ss_value['zhcn_required_component_set'] += self.zhcn(ss_value['required_component_set'][i])[0] + '，'
                ss_value['zhcn_required_component_set'] = ss_value['zhcn_required_component_set'][0:-1]
            self.logic_it('possible_starbase', ss_value)
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
                    ss_value['zhcn_section'] += '※14\\n§H' + self.zhcn(section_name)[0] + '§!，位置：§H'
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


# ================ starbase_buildings 恒星基地建筑 ================
class StarbaseBuildings(ParadoxData):
    def __init__(self):
        super().__init__('starbase_buildings')

    def data_processor(self):
        self.raw_data = self.common_processor('starbase_buildings')
        starbase_buildings_data = self.refinery()
        self.save_data(starbase_buildings_data)
        return starbase_buildings_data

    def refinery(self):
        data = self.raw_data
        for sb_name, sb_value in data.items():
            name = 'sm_' + sb_value['key']
            desc = 'sm_' + sb_value['key'] + '_desc'
            sb_value['zhcn_name'], sb_value['en_name'] = self.zhcn(name)
            sb_value['zhcn_desc'], sb_value['en_desc'] = self.zhcn(desc, True)
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
                self.logic_it('possible', sb_value)
            if 'custom_tooltip' in sb_value:
                sb_value['zhcn_tip'] = self.zhcn(sb_value['custom_tooltip'])[0]
            if 'equipped_component' in sb_value:
                sb_value['equipped_component'] = sb_value['equipped_component'].replace('"', '')
        return data


# ================ starbase_levels 恒星基地等级 ================
class StarbaseLevels(ParadoxData):
    def __init__(self):
        super().__init__('starbase_levels')

    def data_processor(self):
        self.raw_data = self.common_processor('starbase_levels')
        starbase_levels_data = self.refinery()
        self.save_data(starbase_levels_data)
        return starbase_levels_data

    def refinery(self):
        data = self.raw_data
        for sl_name, sl_value in data.items():
            if 'ship_size' in sl_value:
                sl_value['zhcn_name'], sl_value['en_name'] = self.zhcn(sl_value['ship_size'])
            if 'level_weight' in sl_value:
                icon_index = int(sl_value['level_weight']) + 1
                if icon_index > 5:
                    icon_index = 5
                sl_value['icon'] = 'starbase_' + str(icon_index)
        return data


# ================ starbase_modules 恒星基地模块 ================
class StarbaseModules(ParadoxData):
    def __init__(self):
        super().__init__('starbase_modules')

    def data_processor(self):
        self.raw_data = self.common_processor('starbase_modules')
        starbase_modules_data = self.refinery()
        self.save_data(starbase_modules_data)
        return starbase_modules_data

    def refinery(self):
        data = self.raw_data
        for sm_name, sm_value in data.items():
            name = 'sm_' + sm_value['key']
            desc = 'sm_' + sm_value['key'] + '_desc'
            sm_value['zhcn_name'], sm_value['en_name'] = self.zhcn(name)
            sm_value['zhcn_desc'], sm_value['en_desc'] = self.zhcn(desc, True)
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
                self.logic_it('possible', sm_value)
            if 'show_in_tech' in sm_value:
                sm_value['prerequisites'] = ['']
                sm_value['prerequisites'][0] = sm_value['show_in_tech'].replace('"', '')
            self.logic_it('triggered_country_modifier', sm_value)
            self.logic_it('produced_resource_trigger', sm_value)
            if 'icon' not in sm_value:
                sm_value['icon'] = 'starbase_' + sm_value['key']
        return data


# ================ star_classes 行星类型 ================
class StarClasses(ParadoxData):
    def __init__(self):
        super().__init__('star_classes')

    def data_processor(self):
        self.raw_data = self.common_processor('star_classes')
        star_classes_data = self.refinery()
        self.save_data(star_classes_data)
        return star_classes_data

    def refinery(self):
        new_data = {}
        for sc_name, sc_value in self.raw_data.items():
            if not ('rl_' in sc_name):
                new_data[sc_name] = sc_value
        data = new_data
        for sc_name, sc_value in data.items():
            key = ''
            # localization debug
            if sc_value['en_name'] == 'sc_t':
                sc_value['zhcn_name'] = '褐矮星'
                sc_value['en_name'] = 'Class T Brown Dwarf'
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
                sc_value['habitable'] = spawn_mult
                if key in self.all_data['planet_classes']:
                    self.all_data['planet_classes'][key]['habitable_odds'] = '宜居行星概率修正：' + spawn_mult
            if 'num_planets' in sc_value:
                if key in self.all_data['planet_classes']:
                    self.all_data['planet_classes'][key]['desc_detail'] += '星系内行星数' \
                                                                           + sc_value['num_planets']['min'] + '~' \
                                                                           + sc_value['num_planets']['max']
            if 'pc_gas_giant' in sc_value:
                sc_value['pc_gas_giant_odds'] = sc_value['pc_gas_giant']['spawn_odds']
            if 'pc_gaia' in sc_value:
                sc_value['pc_gaia_odds'] = sc_value['pc_gaia']['spawn_odds']
            if 'zhcn_modifier' in sc_value:
                if key in self.all_data['planet_classes']:
                    effect = self.zhcn('effects_on_system')[0]
                    self.all_data['planet_classes'][key]['effect'] = effect + self.indentation + sc_value[
                        'zhcn_modifier'] + '</div>'
                    self.all_data['planet_classes'][key]['zhcn_desc'] += '\\n\\n' + \
                                                                         self.all_data['planet_classes'][key]['effect']
                    sc_value['zhcn_modifier'] = self.zhcn('environmental_hazards')[
                                                    0] + '：' + self.indentation + sc_value['zhcn_modifier'] + '</div>'
            if 'spawn_odds' in sc_value:
                if key in self.all_data['planet_classes']:
                    self.all_data['planet_classes'][key]['spawn_odds'] = sc_value['spawn_odds']
            if 'planet' in sc_value and isinstance(sc_value['planet'], list):
                ori = OrderedDict()
                planet_list = []
                for index in range(len(sc_value['planet'])):
                    ori[index] = sc_value['planet'][index]
                    planet_list.append(sc_value['planet'][index]['key'])
                ori['key'] = planet_list
                sc_value['planet'] = ori
        return data


# ================ static_modifiers 修正 ================
class StaticModifiers(ParadoxData):
    def __init__(self):
        super().__init__('static_modifiers')

    def data_processor(self):
        self.raw_data = self.common_processor('static_modifiers')
        static_modifiers_data = self.refinery()
        self.save_data(static_modifiers_data)
        return static_modifiers_data

    def refinery(self):
        non_include = ['modifier', 'icon_frame', 'icon', 'key', 'main_category', 'zhcn_name', 'zhcn_desc', 'en_name',
                       'en_desc', 'version',
                       # special on 2.2
                       'show_only_custom_tooltip', 'custom_tooltip', 'apply_modifier_to_other_planets']
        refined_data = OrderedDict()
        for sm_name, sm_value in self.raw_data.items():
            sm_value['modifier'] = OrderedDict()
            for key in sm_value:
                if not (key in non_include):
                    sm_value['modifier'][key] = sm_value[key]
            refined_data[sm_name] = OrderedDict()
            for key in non_include:
                if key in sm_value:
                    refined_data[sm_name][key] = self.raw_data[sm_name][key]
        for sm_name, sm_value in refined_data.items():
            if 'custom_tooltip' in sm_value:
                custom_tooltip = self.modifier_processor(self.zhcn(sm_value['custom_tooltip'])[0])
            else:
                custom_tooltip = ''
            sm_value['zhcn_modifier'] = self.modifier_processor(sm_value['modifier'])
            if 'show_only_custom_tooltip' in sm_value and sm_value['show_only_custom_tooltip'] == 'yes' \
                    and len(custom_tooltip) > 0:
                sm_value['zhcn_modifier'] = custom_tooltip
            else:
                sm_value['zhcn_modifier'] += custom_tooltip
        return refined_data


# ================ strategic_resources 战略资源 ================
class StrategicResources(ParadoxData):
    def __init__(self):
        super().__init__('strategic_resources')

    def data_processor(self):
        self.raw_data = self.common_processor('strategic_resources')
        strategic_resources_data = self.refinery()
        self.save_data(strategic_resources_data)
        return strategic_resources_data

    def refinery(self):
        data = self.raw_data
        for sr_name, sr_value in data.items():
            # if 'AI_category' in sr_value:
            #     sr_value['zhcn_AI_category'], sr_value['en_AI_category'] = self.zhcn(sr_value['AI_category'])
            #     Danteng.log(sr_value['zhcn_AI_category'])
            if sr_value['zhcn_name'] == 'time':
                sr_value['zhcn_name'] = '时间'
            if 'deficit_modifier' in sr_value:
                sr_value['zhcn_deficit_modifier'] = self.zhcn(sr_value['deficit_modifier'])[0]
            if 'visibility_prerequisite' in sr_value:
                sr_value['visibility_logic'] = self.modifier_replace(self.logic_processor(
                    sr_value['visibility_prerequisite'])[0])
        return data


# ================ Subjects 附庸 ================
class Subjects(ParadoxData):
    def __init__(self):
        super().__init__('subjects')

    def data_processor(self):
        self.raw_data = self.common_processor('subjects')
        subjects_data = self.refinery()
        self.save_data(subjects_data)
        return subjects_data

    def refinery(self):
        data = self.raw_data
        for name, value in data.items():
            name = 'subject_' + value['key']
            desc = 'subject_desc_' + value['key']
            value['zhcn_name'], value['en_name'] = self.zhcn(name)
            value['zhcn_desc'], value['en_desc'] = self.zhcn(desc, True)
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
            self.logic_it('effect', value)
            self.logic_it('become_vassal', value)
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
                value['zhcn_name'], value['en_name'] = self.zhcn('satrapy_of_horde')
                value['zhcn_desc'], value['en_desc'] = self.zhcn('satrapy_of_horde_desc', True)
            value['effect_logic'] = re.sub(r'From', r'附庸方', value['effect_logic'])
            value['effect_logic'] = re.sub(r'who', r'设定：', value['effect_logic'])
            if 'subject_tax_rate' in value:
                for item in value['subject_tax_rate']:
                    value['tax_rate'] = ''
                    if item in pdx_resource:
                        value['tax_rate'] += '£' + pdx_resource[item] + value['subject_tax_rate'][item]
            if 'overlord_resources' in value and 'produces' in value['overlord_resources']:
                for item in value['overlord_resources']['produces']:
                    value['overlord_produces'] = ''
                    if item in pdx_resource:
                        value['overlord_produces'] += '£' + pdx_resource[item] + \
                                                      value['overlord_resources']['produces'][item]
        return data


# ================ technology 科技 ================
class Technology(ParadoxData):
    def __init__(self):
        super().__init__('technology')

    def data_processor(self):
        self.raw_data = self.common_processor('technology')
        technology_data = self.refinery()
        self.save_data(technology_data)
        return technology_data

    def refinery(self):
        data = self.raw_data
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
                tech_value['zhcn_category'] = self.i18n_zhcn_map[tech_value['category']]
            if 'feature_flags' in tech_value:
                temp_feature = ''
                for i in range(len(tech_value['feature_flags'])):
                    temp_feature += '§H解锁特性：§!' + self.zhcn('feature_' + tech_value['feature_flags'][i])[0] + '\\n'

                if 'zhcn_modifier' in tech_value:
                    if tech_value['zhcn_modifier'][-2:] == '\\n':
                        tech_value['zhcn_modifier'] += temp_feature
                    else:
                        tech_value['zhcn_modifier'] += '\\n' + temp_feature
                else:
                    tech_value['zhcn_modifier'] = temp_feature
            if 'feature_flags' in tech_value:
                if type(tech_value['feature_flags']) == str:
                    tech_value['zhcn_feature_flags'] = self.zhcn('feature_' + tech_value['feature_flags'])[0]
                elif type(tech_value['feature_flags']) == list:
                    tech_value['zhcn_feature_flags'] = ''
                    for i in range(len(tech_value['feature_flags'])):
                        tech_value['zhcn_feature_flags'] += self.zhcn('feature_' + tech_value['feature_flags'][i])[0]
                else:
                    z = 3
            if 'gateway' in tech_value:
                tech_value['zhcn_gateway'] = self.zhcn('gateway_' + tech_value['gateway'])[0]
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
                                tech_value['zhcn_modifier'] = temp + self.zhcn(string)[0]
                        else:
                            string = tech_value['prereqfor_desc'][item]['title'].replace('"', '')
                            tech_value['zhcn_modifier'] = temp + self.zhcn(string)[0]
                Danteng.log(tech_value['zhcn_modifier'])
            if tech_value['zhcn_modifier'][0:2] == '\\n':
                tech_value['zhcn_modifier'] = tech_value['zhcn_modifier'][2:]
            if 'is_dangerous' in tech_value and type(tech_value['is_dangerous']) != str:
                tech_value['is_dangerous'] = tech_value['is_dangerous'][len(tech_value['is_dangerous']) - 1]
            if tech_name in self.tech_prerequisites:
                tech_value['unlock'] = self.tech_prerequisites[tech_name]
                z = 2
        # #     tech_url = 'https://cdn.huijiwiki.com/qunxing/index.php?title=special:redirect/file/' + tech_value['key'] \
        # #                + '.png'
        # #     tech_icon[tech_value['key']] = requests.get(tech_url).url
        # # tech_json = json.dumps(tech_icon, ensure_ascii=False)
        # with open('json\\tech_icon.json', 'w', encoding='UTF-8') as f:
        #     f.write(tech_json)
        return data


# ================ Terraform 地貌改造 ================
class Terraform(ParadoxData):
    def __init__(self):
        super().__init__('terraform')

    def data_processor(self):
        self.raw_data = self.common_processor('terraform')
        terraform_data = self.refinery()
        self.save_data(terraform_data)
        return terraform_data

    def refinery(self):
        data = self.raw_data
        for terraform_name, terraform_value in data.items():
            if ('from' in terraform_value) and ('to' in terraform_value):
                terraform_value['from_icon'] = self.all_data['planet_classes'][terraform_value['from']]['icon']
                terraform_value['to_icon'] = self.all_data['planet_classes'][terraform_value['to']]['icon']
                tf, tf_en = self.zhcn(terraform_value['from'])
                tt, tt_en = self.zhcn(terraform_value['to'])
                terraform_value['zhcn_name'] = tf + '→' + tt
                terraform_value['en_name'] = tf_en + ' to ' + tt_en
        return data


# ================ traditions 传统 ================
class Traditions(ParadoxData):
    def __init__(self):
        super().__init__('traditions')

    def data_processor(self):
        self.raw_data = self.common_processor('traditions')
        traditions_data = self.refinery()
        self.save_data(traditions_data)
        return traditions_data

    def refinery(self):
        data = self.raw_data
        tr_sw_key = []
        for tr_name, tr_value in data.items():
            tr_value['icon'] = re.sub(r'^tr_', r'tradition_', tr_value['key'])
            if 'tradition_swap' in tr_value:
                if type(tr_value['tradition_swap']) != list:
                    temp = [tr_value['tradition_swap']]
                    tr_value['tradition_swap'] = temp
                for i in range(len(tr_value['tradition_swap'])):
                    tr_value['tradition_swap'][i]['key'] = tr_value['key']
                    tr_value['tradition_swap'][i]['main_category'] = 'traditions'
                    tr_value['tradition_swap'][i]['version'] = self.version
                    tr_swap_name = tr_value['tradition_swap'][i]['name']
                    tr_value['tradition_swap'][i]['zhcn_name'], tr_value['tradition_swap'][i]['en_name'] = self.zhcn(
                        tr_swap_name)
                    tr_value['tradition_swap'][i]['zhcn_desc'], tr_value['tradition_swap'][i]['en_desc'] = self.zhcn(
                        tr_swap_name + '_desc', True)
                    tr_value['tradition_swap'][i]['icon'] = re.sub(r'^tr_', r'tradition_', tr_value['tradition_swap'][
                        i]['name'])
                    if 'inherit_icon' in tr_value['tradition_swap'][i] and \
                            tr_value['tradition_swap'][i]['inherit_icon'] == 'yes':
                        tr_value['tradition_swap'][i]['icon'] = tr_value['icon']
                    if '_finish' in tr_value['key'] or '_adopt' in tr_value['key']:
                        Danteng.log('传统的key：' + tr_value['key'])
                        tr_value['tradition_swap'][i]['icon'] = 'Menu_icon_traditions'
                    self.logic_it('trigger', tr_value['tradition_swap'][i])
                    if 'modifier' in tr_value['tradition_swap'][i]:
                        Danteng.log('\n' + tr_value['tradition_swap'][i]['zhcn_name'] + '的modifier：' + 'modifier')
                        tr_value['tradition_swap'][i]['zhcn_modifier'] = self.modifier_processor(
                            tr_value['tradition_swap'][i]['modifier'])
                    self.logic_it('weight', tr_value['tradition_swap'][i])
                    for key in tr_value['tradition_swap'][i]:
                        if key not in tr_sw_key:
                            tr_sw_key.append(key)
            if '_finish' in tr_value['key'] or '_adopt' in tr_value['key']:
                tr_value['icon'] = 'Menu_icon_traditions'
            if tr_name in self.all_data['tradition_categories']:
                tr_value['category'] = self.all_data['tradition_categories'][tr_name]
                tr_value['zhcn_category'] = self.zhcn(self.all_data['tradition_categories'][tr_name])[0]
        return data


# ================ tradition_category 传统分类 ================
class TraditionCategory(ParadoxData):
    def __init__(self):
        super().__init__('tradition_categories')

    def data_processor(self):
        self.raw_data = self.common_processor('tradition_categories')
        return self.refinery()

    def refinery(self):
        refined_data = {}
        for tc_name, tc_value in self.raw_data.items():
            for i in range(len(tc_value['traditions'])):
                refined_data[tc_value['traditions'][i].replace('"', '')] = tc_name
            refined_data[tc_value['adoption_bonus'].replace('"', '')] = tc_name
            refined_data[tc_value['finish_bonus'].replace('"', '')] = tc_name
        return refined_data


# ================ Traits 特性 ================
class Traits(ParadoxData):
    def __init__(self):
        super().__init__('traits')

    def data_processor(self):
        self.raw_data = self.common_processor('traits')
        traits_data = self.refinery()
        self.save_data(traits_data)
        return traits_data

    def refinery(self):
        data = self.raw_data
        for traits_name, traits_value in data.items():
            # localization debug
            if traits_value['en_name'] == 'trait_pc_machine_preference':
                traits_value['en_name'] = '适应机械星球'
                traits_value['en_name'] = 'Machine World Preference'
            if traits_value['en_name'] == 'trait_pc_hive_preference':
                traits_value['en_name'] = '适应蜂巢星球'
                traits_value['en_name'] = 'Hive World Preference'
            if 'allowed_archetypes' in traits_value:
                find = re.findall(r'(\S+)', traits_value['allowed_archetypes'][0])
                if find:
                    traits_value['allowed_archetypes'] = find
                traits_value['zhcn_archetypes'] = list.copy(traits_value['allowed_archetypes'])
                for i in range(len(traits_value['zhcn_archetypes'])):
                    traits_value['zhcn_archetypes'][i] = self.zhcn(traits_value['zhcn_archetypes'][i])[0]
            if 'custom_tooltip' in traits_value:
                traits_value['zhcn_modifier'] = self.zhcn(traits_value['custom_tooltip'])[0]
            elif 'zhcn_self_modifier' in traits_value:
                traits_value['zhcn_modifier'] = traits_value['zhcn_self_modifier']
            elif 'assembling_modifier' in traits_value:
                traits_value['zhcn_modifier'] = self.zhcn(traits_value['assembling_modifier'])[0]
            if 'ai_categories' in traits_value:
                for i in range(len(traits_value['ai_categories'])):
                    traits_value['ai_categories'][i] = self.zhcn(traits_value['ai_categories'][i])[0]
            self.logic_it('leader_potential_add', traits_value)
            self.logic_it('species_potential_add', traits_value)
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
                    traits_value['zhcn_leader_class'][i] = self.zhcn(traits_value['leader_class'][i])[0]
            if 'slave_cost' in traits_value:
                traits_value['slave_cost_detail'] = ''
                for sub_name, sub_value in traits_value['slave_cost'].items():
                    traits_value['slave_cost_detail'] += '£' + sub_name + sub_value
        return data


# ================ war_goals 战争目标 ================
class WarGoals(ParadoxData):
    def __init__(self):
        super().__init__('war_goals')

    def data_processor(self):
        self.raw_data = self.common_processor('war_goals')
        war_goals_data = self.refinery()
        self.save_data(war_goals_data)
        return war_goals_data

    def refinery(self):
        data = self.raw_data
        for wg_name, wg_value in data.items():
            name = 'war_goal_' + wg_value['key']
            desc = 'war_goal_' + wg_value['key'] + '_desc'
            wg_value['zhcn_name'], wg_value['en_name'] = self.zhcn(name)
            wg_value['zhcn_desc'], wg_value['en_desc'] = self.zhcn(desc, True)
            if 'on_accept' in wg_value:
                self.logic_it('on_accept', wg_value)
                wg_value['on_accept_logic'] = wg_value['on_accept_logic'] \
                    .replace('[Root.GetName]', '进攻方') \
                    .replace('[From.GetName]', '防御方') \
                    .replace('[Root.GetAdj]', '进攻方的')
            if 'on_status_quo' in wg_value:
                self.logic_it('on_status_quo', wg_value)
                wg_value['on_status_quo_logic'] = wg_value['on_status_quo_logic'] \
                    .replace('[Root.GetName]', '进攻方') \
                    .replace('[From.GetName]', '防御方') \
                    .replace('[Root.GetAdj]', '进攻方的')
            if 'on_wargoal_set' in wg_value:
                self.logic_it('on_wargoal_set', wg_value)
                wg_value['on_wargoal_set_logic'] = wg_value['on_wargoal_set_logic'] \
                    .replace('[Root.GetName]', '进攻方') \
                    .replace('[From.GetName]', '防御方') \
                    .replace('[Root.GetAdj]', '进攻方的')
            if 'possible' in wg_value:
                wg_value.pop('possible_desc')
                self.logic_it('possible', wg_value)
        return data


# ================ Events 事件 ================
class Events(ParadoxData):
    def __init__(self):
        super().__init__('events')

    def data_processor(self):
        self.raw_data = self.common_processor('events', False)
        events_data = self.refinery()
        self.save_data(events_data)
        return events_data

    def refinery(self):
        refined_data = OrderedDict()
        temp = OrderedDict()
        for name, value in self.raw_data.items():
            value['id'] = value['id'].replace('"', '')
            ids = value['id']
            value['key'] = ids
            if 'title' in value:
                value['title'] = value['title'].replace('"', '')
                value['zhcn_name'], value['en_name'] = self.zhcn(value['title'], True)
                if 'desc' in value and type(value['desc']) == str:
                    value['desc'] = value['desc'].replace('"', '')
                    value['zhcn_desc'], value['en_desc'] = self.zhcn(value['desc'], True)
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
                            Danteng.log('未处理的事件描述：' + ids)
                            desc = ''
                        zh_desc, en_desc = self.zhcn(desc, True)
                        value['zhcn_desc'].append(zh_desc)
                        value['en_desc'].append(en_desc)
                else:
                    value['zhcn_desc'], value['en_desc'] = self.zhcn(value['id'] + '.desc', True)
            else:
                value['zhcn_name'] = '无标题'
                value['en_name'] = 'No Title'
                value['zhcn_desc'] = '无描述'
                value['en_desc'] = 'No Description'
            if 'picture' in value:
                if type(value['picture']) == str:
                    value['picture'] = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', value['picture'].replace('"', ''))
                    if value['picture'] in self.icon_dict:
                        value['picture'] = self.icon_dict[value['picture']]['icon']
                elif type(value['picture']) == list:
                    for i in range(len(value['picture'])):
                        picture = value['picture'][i]['picture']
                        picture = re.sub(r'.*?/(.[^/]*?)\..*', r'\1', picture.replace('"', ''))
                        if picture in self.icon_dict:
                            value['picture'][i]['picture'] = self.icon_dict[picture]['icon']
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
                        option[i]['zhcn_name'], option[i]['en_name'] = self.zhcn(option[i]['name'])
                        option[i]['zhcn_desc'], option[i]['zhcn_desc'] = self.zhcn(option[i]['name'] + '.tooltip')
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
                                        ethic_icon = ethic_icon + '[[File:' + trigger['has_ethic'][j] \
                                            .replace('"', '') + '.png|16px|link=]]'
                                    option[i]['zhcn_name'] = ethic_icon + option[i]['zhcn_name']
                                    option[i]['en_name'] = ethic_icon + option[i]['en_name']
                                    Danteng.log('Cace 2 :' + ethic_icon)
                            elif 'OR' in trigger and 'has_ethic' in trigger['OR']:
                                ethic_icon = ''
                                if type(trigger['OR']['has_ethic']) == str:
                                    ethic_icon = ethic_icon + '[[File:' + trigger['OR']['has_ethic'] \
                                        .replace('"', '') + '.png|16px|link=]]'
                                    Danteng.log('Cace 3.1 :' + ethic_icon)
                                else:
                                    for j in range(len(trigger['OR']['has_ethic'])):
                                        ethic_icon = ethic_icon + '[[File:' + trigger['OR']['has_ethic'][j] \
                                            .replace('"', '') + '.png|16px|link=]]/'
                                    ethic_icon = ethic_icon[0:-1]
                                    option[i]['zhcn_name'] = ethic_icon + option[i]['zhcn_name']
                                    option[i]['en_name'] = ethic_icon + option[i]['en_name']
                                    Danteng.log('Cace 3.2 :' + ethic_icon)
                value['option'] = option
            self.logic_it('trigger', value)
            self.logic_it('immediate', value)
            self.logic_it('mean_time_to_happen', value)
            refined_data[value['id']] = value
        return refined_data


# ================ Special ================
# ================ achievements 成就 ================
class Achievements(ParadoxData):
    def __init__(self):
        super().__init__('achievements')

    def data_processor(self):
        self.raw_data = self.text_processor('achievements.txt')
        achievements_data = self.refinery()
        self.save_data(achievements_data)
        return achievements_data

    def refinery(self):
        data = self.raw_data
        refined_data = {}
        achievement_url = r'http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=9C7BD9BC032EA645C1BB3EF672B80E5D&appid=281990'
        has_got_data = False
        json_request = ''
        while not has_got_data:
            try:
                json_request = requests.get(achievement_url)
                Danteng.log('已获取' + achievement_url)
                has_got_data = True
            except:
                Danteng.log('获取出现错误，1秒后重试...')
                time.sleep(1)
        json_data = json_request.content
        achievement_dict = json.loads(json_data)
        achievement_data = achievement_dict['game']['availableGameStats']['achievements']
        achievements = OrderedDict()
        for i in range(len(achievement_data)):
            item = achievement_data[i]
            item.pop('icon')
            item.pop('icongray')
            achievements[item['name']] = item
        for name, value in data.items():
            value['key'] = value['sub_category']
            value.update(achievements[value['key']])
            if 'id' in value:
                value['_index'] = value['id']
            self.logic_it('possible', value)
            self.logic_it('happened', value)
            refined_data[value['key']] = value
        icon_dict = {
            'achievement_queening': 'swarm',
            'achievement_rift_sealed': 'exd',
            'achievement_synth_detector': 'ai',
            'achievement_wraith': 'warrior_of_light',
            'achievement_slave_to_the_system': 'slave_to_the_systems',
            'achievement_planned_obsolesence': 'planned_obsolescence',
            'achievement_omniculture': 'omnivultural',
            'achievement_ringineering': 'ringworld_engineers',
            'achievement_habitat_at_the_end_of_the_universe': 'view_from_the_end_of_the_world',
            'achievement_scrapper': 'who_scraps_the_scrapper',
            'achievement_hatchling': '1999_ad',
            'achievement_tiyanki': 'a_hump_like_a_snow_hill',
            'achievement_amoeba': 'it_followed_me_home',
            'achievement_l-cluster': 'and_hope',
            'achievement_galatron': 'indescribable_power',
        }
        for name, value in refined_data.items():
            if name in icon_dict:
                value['icon'] = icon_dict[name]
            else:
                index = name.find('_')
                icon = name[(index + 1):]
                value['icon'] = icon
            value['name'] = value['displayName']
            value['zhcn_name'] = value['displayName']
            value['en_name'] = value['displayName']
            value.pop('sub_category')
            value['zhcn_desc'] = value['description']
            value['en_desc'] = value['description']
            value['main_category'] = self.item_category
            value['version'] = self.version
        return refined_data


# ================ scripted variables 预置变量 ================
class ScriptedVariables(ParadoxData):
    def __init__(self):
        super().__init__('global')

    def data_processor(self):
        common_path = self.base_path + 'common\\'
        category_path = 'scripted_variables'
        for filename in os.listdir(os.path.join(common_path, category_path)):
            if filename[-4:] == '.txt':
                pp = ParadoxParser(os.path.join(common_path, category_path, filename), self.item_category)
                self.raw_data.update(pp.get_data()[1])
        scripted_variables = self.refinery()
        self.set_scripted_variables(scripted_variables)
        return scripted_variables

    def refinery(self):
        return self.raw_data


# ================ Interface 图标 ================
class Interface(ParadoxData):
    def __init__(self):
        super().__init__('interface')

    def data_processor(self):
        icons_data = OrderedDict()
        icon_list = ['icons', 'eventpictures', 'relics_view']
        for name in icon_list:
            path = self.base_path + 'interface\\' + name + '.gfx'
            icons = self.text_processor(path)
            self.raw_data = icons
            icons_data.update(self.refinery())
            self.save_data(icons_data)
        self.set_icons(icons_data)
        return icons_data

    def refinery(self):
        for name in self.raw_data['spriteTypes']:
            data = self.raw_data['spriteTypes'][name]
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
