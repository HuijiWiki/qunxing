from collections import OrderedDict

from CommonFile import CommonFile


# ####################### Special #######################
# scripted_triggers
class ScriptedTriggers(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        return processed


# Icons
class Interface(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version, False)
        # ['name', 'textureFile', 'noOfFrames', 'texturefile', 'masking_texture', 'alwaystransparent']
        z = 1

    def merge(self, raw_file):
        for filename in raw_file:
            if 'spriteTypes' not in raw_file[filename]:
                raise Exception('SpriteTypesError')
            if 'spriteType' not in raw_file[filename]['spriteTypes']:
                raise Exception('SpriteTypeError')
            for i in range(len(raw_file[filename]['spriteTypes']['spriteType'])):
                raw = raw_file[filename]['spriteTypes']['spriteType'][i]
                item = OrderedDict()
                for name in raw:
                    if name == 'texturefile' or name == 'textureFile':
                        item['textureFile'] = raw[name].replace('"', '').split('/')[-1].split('.')[0]
                    else:
                        item[name] = raw[name].replace('"', '')
                self.refined[item['name']] = item

    def analysis(self, raw):
        return raw

    def post_process(self):
        super().post_process()
        self.icon_dict = self.data


# achievements
# achievements.txt


# ####################### Common #######################
# agendas
class Agendas(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        return processed


# ai_budget
# alerts.txt
# ambient_objects
# anomalies
# archaeological_site_types
# armies
# artifact_actions
# ascension_perks
# asteroid_belts
# attitudes
# bombardment_stances
# buildings
# button_effects
# bypass
# casus_belli
# colony_automation
# colony_automation_exceptions
# colony_types
# colors
# component_sets
# component_slot_templates
# component_tags
# component_templates
# country_customization
# country_types
# decisions
# defines


# deposits
class Deposits(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version, False)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        if 'category' in raw:
            if raw['category'] in self.all_data['deposit_categories']:
                processed.update(self.all_data['deposit_categories'][raw['category']])
        self.logic_it(raw, processed, 'on_cleared', 'on_cleared_logic')
        self.logic_it(raw, processed, 'can_be_cleared', 'can_be_cleared_logic')
        return processed


# deposit_categories
class DepositCategories(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version, False)
        # ['blocker', 'important']
        z = 1

    def post_process(self):
        for name in self.data:
            self.data[name].pop('key')
            self.data[name].pop('file')

# diplomacy_economy
# diplomatic_actions
# diplo_phrases
# districts
# economic_categories
# economic_plans
# edicts


# ethics
class Ethics(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        if 'tags' in raw:
            processed['instruction'], processed['en_instruction'] = self.modifier(raw, 'tags')
        if 'pop_attraction_tag' in raw:
            for i in range(len(raw['pop_attraction_tag'])):
                processed['pop_attraction_tag'][i]['zhcn_desc'], processed['pop_attraction_tag'][i]['en_desc'] = \
                    self.localise(raw['pop_attraction_tag'][i]['desc'], 'cn')
                processed['pop_attraction_tag'][i]['zhcn_trigger'] = \
                    self.logic(raw['pop_attraction_tag'][i], 'trigger')
        return processed

    def post_process(self):
        self.data.pop('ethic_categories')
        super().post_process()


# event_chains
# fallen_empires
# federation_laws
# federation_law_categories
# federation_perks
# federation_types
# galactic_focuses
# game_rules
# global_ship_designs


# governments & civics & authorities & origin
class GovSeries:
    def __init__(self, raw_file, category, all_loc, version):
        gov_raw = OrderedDict()
        ori_raw = OrderedDict()
        gov_raw['00_governments.txt'] = raw_file['00_governments.txt']
        auth_raw = raw_file['authorities']
        ori_raw['00_origins.txt'] = raw_file['civics']['00_origins.txt']
        civ_raw = raw_file['civics']
        civ_raw.pop('00_origins.txt')
        gov_series = {
            'governments': {'func': Governments, 'data': gov_raw},
            'civics': {'func': Civics, 'data': civ_raw},
            'authorities': {'func': Authorities, 'data': auth_raw},
            'origins': {'func': Origins, 'data': ori_raw},
        }
        self.data = OrderedDict()
        for name in gov_series:
            self.data[name] = gov_series[name]['func'](gov_series[name]['data'], name, all_loc, version)


# governments
class Governments(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        num_keys = ['use_regnal_names', 'dynastic_last_names', 'should_force_rename', ]
        text_list = {'ruler_title': ['zhcn_ruler', 'en_ruler'],
                     'ruler_title_female': ['zhcn_ruler_female', 'en_ruler_female'],
                     'heir_title': ['zhcn_heir', 'en_heir'],
                     'heir_title_female': ['zhcn_heir_female', 'en_heir_female'],
                     'leader_class': ['zhcn_leader_class', 'en_leader_class']}
        for name in text_list:
            if name in processed:
                processed[text_list[name][0]] = self.localise(processed[name], 'cn')[0]
                processed[text_list[name][1]] = self.localise(processed[name], 'en')[0]
        return processed


# governments/authorities
class Authorities(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        postfix_list = ['hive_mind', 'machine_intelligence', 'corporate']
        # ['election_term_years', 're_election_allowed', 'election_type', 'uses_mandates', 'tags',
        # 'can_have_emergency_elections', 'emergency_election_cost', 'max_election_candidates', 'has_agendas',
        # 'has_heir', 'has_factions', 'can_reform', 'localization_postfix', 'valid_for_released_vassal',
        # 'playable', 'traits', 'machine_empire']
        if 'localization_postfix' in raw:
            if raw['localization_postfix'] not in postfix_list:
                z = 6
        if 'is_origin' in raw and raw['is_origin'] == 'yes':
            raise Exception('FoundOriginNotAuthority')
        return processed


# governments/civics
class Civics(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        # ['modification', 'playable', 'swap_type', 'has_secondary_species', 'starting_colony']
        if 'swap_type' in raw:
            if 'name' in raw['swap_type']:
                processed['swap_type']['zhcn_name'] = self.localise(raw['swap_type']['name'], 'cn')[0]
                processed['swap_type']['en_name'] = self.localise(raw['swap_type']['name'], 'en')[0]
                processed['swap_type']['zhcn_desc'] = self.localise(raw['swap_type']['name'] + '_desc', 'cn')[0]
                processed['swap_type']['en_desc'] = self.localise(raw['swap_type']['name'] + '_desc', 'en')[0]
            if 'description' in raw['swap_type']:
                processed['swap_type']['zhcn_more_desc'] = self.localise(raw['swap_type']['description'], 'cn')[0]
                processed['swap_type']['en_more_desc'] = self.localise(raw['swap_type']['description'], 'en')[0]
            if 'trigger' in raw['swap_type']:
                processed['swap_type']['zhcn_trigger'] = self.logic(raw['swap_type'], 'trigger')
        if 'has_secondary_species' in raw:
            if 'title' in raw['has_secondary_species']:
                processed['has_secondary_species']['zhcn_name'] = self.localise(
                    raw['has_secondary_species']['title'], 'cn')[0]
                processed['has_secondary_species']['en_name'] = self.localise(
                    raw['has_secondary_species']['title'], 'en')[0]
        return processed


# governments/origins
class Origins(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        if 'is_origin' not in raw or raw['is_origin'] != 'yes':
            raise Exception('FoundOriginNotAuthority')
        if 'picture' in raw:
            if raw['picture'] in self.all_data['gfx']:
                raw['picture'] = self.all_data['gfx'][raw['picture']]['textureFile']
                z = 4
        if 'has_secondary_species' in raw:
            title = raw['has_secondary_species']['title']
            processed['has_secondary_species']['zhcn_name'] = self.localise(title, 'cn')[0]
            processed['has_secondary_species']['en_name'] = self.localise(title, 'en')[0]
        if 'flags' in raw:
            raw['flags'] = raw['flags'][0].split(' ')
        if 'initializers' in raw:
            raw['initializers'] = raw['initializers'][0].split(' ')
        return processed


# graphical_culture
# HOW_TO_MAKE_NEW_SHIPS.txt
# lawsuits
# leader_classes
# mandates
# map_modes
# megastructures
# message_types.txt
# name_lists
# notification_modifiers
# observation_station_missions
# on_actions
# opinion_modifiers
# personalities
# planet_classes
# planet_modifiers
# policies
# pop_categories


# pop_faction_types
class PopFactionTypes(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)

        # 'demand', 'actions'

        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        keys = ['is_potential', 'parameters', 'can_join_pre_triggers', 'can_join_faction', 'attraction', 'leader',
                'on_create', 'on_destroy']
        for key in keys:
            self.logic_it(raw, processed, key, key + '_logic')
        if 'demand' in raw:
            for i in range(len(raw['demand'])):
                z = 5
            z = 4
        z = 3

# pop_jobs
# precursor_civilizations
# random_names
# relics
# resolutions
# resolution_categories
# scripted_effects
# scripted_loc
# scripted_triggers                     done
# scripted_variables
# section_templates
# sector_focuses
# sector_types
# ship_behaviors
# ship_sizes
# solar_system_initializers
# special_projects
# species_archetypes
# species_classes
# species_names
# species_rights
# starbase_buildings
# starbase_levels
# starbase_modules
# starbase_types
# start_screen_messages
# star_classes
# static_modifiers


# strategic resources
class StrategicResources(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1
    # 'deficit_modifier'→ Static Modifiers


# subjects
class Subjects(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        if 'subject_tax_rate' in raw:
            processed['tax_rate'] = ''
            for name in raw['subject_tax_rate']:
                processed['tax_rate'] += '£' + name + raw['subject_tax_rate'][name]
        if 'effect' in raw:
            processed['effect_logic'] = self.logic(raw, 'effect')
        if 'overlord_resources' in raw:
            processed['overlord_produces'] = ''
            for name in raw['overlord_resources']['produces']:
                processed['overlord_produces'] += '£' + name + raw['overlord_resources']['produces'][name]
        if 'become_vassal' in raw:
            processed['become_vassal_logic'] = self.logic(raw, 'become_vassal')
        return processed

# system_types
# technology
# terraform
# trade_conversions
# traditions
# tradition_categories


# traits
class Traits(CommonFile):
    def __init__(self, raw_file, category, all_loc, version):
        super().__init__(raw_file, category, all_loc, version)
        z = 1

    def analysis(self, raw):
        processed = super().analysis(raw)
        num_keys = ['cost', 'modification', 'initial', 'randomized', 'immortal_leaders', 'hide_age', 'sorting_priority',
                    'forced_happiness', 'leader_age_min', 'leader_age_max', 'potential_crossbreeding_chance', 'sapient',
                    'advanced_trait', 'slave_cost', 'improves_leaders']
        self.split_list(raw, processed, 'allowed_archetypes', 'zhcn_archetypes', 'en_archetypes')
        self.split_list(raw, processed, 'leader_trait', 'zhcn_trait', 'en_trait')
        self.split_list(raw, processed, 'leader_class', 'zhcn_leader', 'en_leader')
        if 'ai_categories' in raw:
            processed['cn_ai_cat'] = []
            processed['en_ai_cat'] = []
            for i in range(len(raw['ai_categories'])):
                processed['cn_ai_cat'].append(self.localise(raw['ai_categories'][i], 'cn')[0])
                processed['en_ai_cat'].append(self.localise(raw['ai_categories'][i], 'en')[0])
        self.split_list(raw, processed, 'opposites')
        # modifier要合并吗？custom_tooltip，modifier，self_modifier等
        # cost要写中文吗？
        # for traits_name, traits_value in data.items():
        #     if 'slave_cost' in traits_value:
        #         traits_value['slave_cost_detail'] = ''
        #         for sub_name, sub_value in traits_value['slave_cost'].items():
        #             traits_value['slave_cost_detail'] += '£' + sub_name + sub_value
        return processed

    def post_process(self):
        pass


# war_goals

# ####################### Events #######################
