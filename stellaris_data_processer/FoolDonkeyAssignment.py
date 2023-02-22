# 用于处理正常人无法理解的蠢驴思维
# 用到的时候再加
# 作为"静态"变量文件使用

# 蠢驴无法自动化对应的本地化变量只能手动对应
from danteng import Danteng
import re

pdx_replace_dict = {
    'envoys_add': 'MOD_COUNTRY_ENVOYS_ADD',
    'survey': 'SURVEY_ORDER',
    'is_asteroid': 'PLANET_IS_ASTEROID',
}

pdx_manual_dict = {
    'local_human_species_class': {'cn': '玩家种族类型为', 'en': 'player species class'},
    'num_fallen_empires_setting': {'cn': '设定的失落帝国数', 'en': 'number of fallen empires setting'},
    'is_primary_star': {'cn': '是星系主恒星', 'en': 'is primary star'}
}

pdx_replace_dict_2 = {
    'all_technology_research_speed': 'MOD_COUNTRY_ALL_TECH_RESEARCH_SPEED',
    'science_ship_survey_speed': 'ship_science_survey_speed',
    'species_leader_exp_gain': 'leader_species_exp_gain',
    'pop_ethics_shift_speed_mult': 'MOD_POP_ETHICS_SHIFT_SPEED',
    'admiral_skill_levels': 'leader_admiral_skill_levels',
    'ruler_skill_levels': 'leader_ruler_skill_levels',
    'governor_skill_levels': 'leader_governor_skill_levels',
    'slave_mineral_output': 'pop_slave_mineral_output',
    'slave_food_output': 'pop_slave_food_output',
    'shipclass_science_ship_disengage_mult': 'shipclass_science_ship_evasion_add',
    'black_hole_pentagruel_research': 'black_hole_pantagruel',
    'adjacency_bonus': 'ADJACENCY_BONUS',
    'physics': 'PHYSICS',
    'society': 'SOCIETY',
    'engineering': 'ENGINEERING',
    'survey': '调查',
    'caste_system': 'citizenship_caste_system',
    'personality_type_opportunist': '机会主义者',
    'personality_type_caste_system': '阶序制度',
    'personality_type_displacer': '迁移者',
    'personality_type_multispecies': '多种族者',
    'personality_type_crisis_fighter': '危机斗士',
    'personality_type_wants_tribute': '想要贸易',
    'personality_type_decadent': '颓败',
    'attack_neutrals': '攻击中立势力',
    'personality_type_crisis_leader': '危机斗士领导者',
    'personality_type_custodian': '监护者',
    'personality_type_enigmatic': '神秘态度',
    'personality_type_limited': '限制',
    'personality_type_holy_planets': '重视圣地',
    'personality_type_demands_clear_borders': '需要边界缓冲区',
    'personality_type_attack_neutrals': '攻击中立势力',
    'personality_type_berserker': '狂暴',
    'democratic': '民主制',
    'important': '重要',
    'none': '无',
    'MOD_SHIP_AUTO_REPAIR_ADD': '每月船体回复值',
    'requires_technology_glandular_acclimation': '£trigger_no  §R需要£society §Y腺体改造适应§!科技。§!',
    '$NAME_Rampaging_Forest$': 'Rampaging Forests',
    'spawn_chance': '出现概率',
    'trading_hub': 'sm_trading_hub',
    'shipyard': 'sm_shipyard',
    'anchorage': 'sm_anchorage',
    'AI_STRIKE_CRAFT_1': 'AI_STRIKE_CRAFT',
    'station_small_aura_components': '防御平台光环',
    'station_medium_aura_components': '防御平台光环',
    'station_large_aura_components': '防御平台光环',
    'spaceport': '太空港',
    'starbase_shipyard': '船坞',
    'starbase_defenses': '防御',
    'core': '核心',
    'is_ironman': '铁人模式',
}


error_dict = []


# fool_donkey_dict_modifier大辞典处理
def preprocess_pdx_dict(key):
    if not (key in pdx_modifier):
        Danteng.log('蠢驴大辞典注意：' + key + '不在里面，现在处理')
        ori = key
        key = key.lower()
        pdx_modifier[ori] = dict()
        pm_tags = re.findall(r'^district_.*?_max$', key)
        bd_tags = re.findall(r'^building_.*?_max$', key)
        if ('_add' in key) or ('level' in key) or ('add_static' in key):
            pdx_modifier[ori]['positive'] = 'true'
            pdx_modifier[ori]['mode'] = 'add'
        elif ('reduction' in key) or ('cost' in key) or ('upkeep' in key):
            pdx_modifier[ori]['positive'] = 'false'
            pdx_modifier[ori]['mode'] = 'mult'
        elif ('speed' in key) or ('resource' in key) or ('fire_rate_mult' in key) or ('hull_mult' in key) or (
                'damage' in key) or ('attract' in key) or ('output' in key) or ('_habitability' in key) or (
                'damage' in key) or ('produces_mult' in key) or ('job_' in key and '_per_pop' in key):
            pdx_modifier[ori]['positive'] = 'true'
            pdx_modifier[ori]['mode'] = 'mult'
        elif len(pm_tags) == 1 or len(bd_tags) == 1:
            pdx_modifier[ori]['positive'] = 'true'
            pdx_modifier[ori]['mode'] = 'add'
        # elif '_mult' in key:
        #     fool_donkey_dict_modifier[key]['mode'] = 'mult'
        #     fool_donkey_dict_modifier[key]['mode'] = 'mult'
        Danteng.log('它的正负性：' + pdx_modifier[ori]['positive'] +
                    '它的加乘性：' + pdx_modifier[ori]['mode'])


# 一些modifier是否是正向的以及是相乘还是相加
#
# 绿色是§G，红色是§R，闭合是§!
pdx_modifier = {
    # - *
    'empire_size_pops_mult': {'positive': 'false', 'mode': 'mult'},
    'country_war_exhaustion_mult': {'positive': 'false', 'mode': 'mult'},
    'country_trade_fee': {'positive': 'false', 'mode': 'mult'},
    'ship_emergency_ftl_mult': {'positive': 'false', 'mode': 'mult'},
    'planet_clear_blocker_time_mult': {'positive': 'false', 'mode': 'mult'},
    'species_empire_size_mult': {'positive': 'false', 'mode': 'mult'},
    'pop_housing_usage_mult': {'positive': 'false', 'mode': 'mult'},
    'country_subject_power_penalty_mult': {'positive': 'false', 'mode': 'mult'}, # '§Y附属国实力§!对外交关系所产生的效果'
    'empire_size_penalty_mult': {'positive': 'false', 'mode': 'mult'},
    'pop_demotion_time_mult': {'positive': 'false', 'mode': 'mult'},

    # - +

    # + +
    'leader_age': {'positive': 'true', 'mode': 'add'},
    'country_admin_cap_add': {'positive': 'true', 'mode': 'add'},
    'country_leader_pool_size': {'positive': 'true', 'mode': 'add'},

    # + *
    'trade_value_mult': {'positive': 'true', 'mode': 'mult'},
    'pop_happiness': {'positive': 'true', 'mode': 'mult'},
    'pop_citizen_happiness': {'positive': 'true', 'mode': 'mult'},
    'species_leader_exp_gain': {'positive': 'true', 'mode': 'mult'},
    'ship_disengage_chance_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_weapon_range_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_evasion_mult': {'positive': 'true', 'mode': 'mult'},
    'army_disengage_chance_mult': {'positive': 'true', 'mode': 'mult'},
    'army_morale': {'positive': 'true', 'mode': 'mult'},
    'army_experience_gain_mult': {'positive': 'true', 'mode': 'mult'},
    'edict_length_mult': {'positive': 'true', 'mode': 'mult'},
    'country_naval_cap_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_anomaly_generation_chance_mult': {'positive': 'true', 'mode': 'mult'},
    'pop_environment_tolerance': {'positive': 'true', 'mode': 'mult'},
    'pop_growth_from_immigration': {'positive': 'true', 'mode': 'mult'},
    'pop_cat_worker_happiness': {'positive': 'true', 'mode': 'mult'},
    'pop_cat_slave_happiness': {'positive': 'true', 'mode': 'mult'},
    'country_pop_enslaved_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_immigration_pull_mult': {'positive': 'true', 'mode': 'mult'},
    'country_admin_cap_mult': {'positive': 'true', 'mode': 'mult'},
    'diplo_weight_mult': {'positive': 'true', 'mode': 'mult'},
    'pop_amenities_usage_no_happiness_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_pop_assembly_mult': {'positive': 'true', 'mode': 'mult'},
    'empire_size_branch_office_mult': {'positive': 'true', 'mode': 'mult'},
    'branch_office_value_mult': {'positive': 'true', 'mode': 'mult'},
    'empire_size_systems_mult': {'positive': 'true', 'mode': 'mult'},
}

pdx_modifier_2 = {
    # - *
    'pop_amenities_usage_mult': {'positive': 'false', 'mode': 'mult'},
    'job_criminal_per_crime': {'positive': 'false', 'mode': 'mult'},
    'job_deviant_drone_per_crime': {'positive': 'false', 'mode': 'mult'},
    'job_corrupt_drone_per_crime': {'positive': 'false', 'mode': 'mult'},
    'planet_crime_mult': {'positive': 'false', 'mode': 'mult'},
    'planet_pop_assemblers_upkeep_mult': {'positive': 'false', 'mode': 'mult'},
    'pop_cat_slave_political_power': {'positive': 'false', 'mode': 'mult'},
    'planet_crime_no_happiness_mult': {'positive': 'false', 'mode': 'mult'},

    # - +
    'planet_crime_add': {'positive': 'false', 'mode': 'add'},
    'job_criminal_add': {'positive': 'false', 'mode': 'add'},
    'job_deviant_drone_add': {'positive': 'false', 'mode': 'add'},
    'job_corrupt_drone_add': {'positive': 'false', 'mode': 'add'},
    'pop_housing_usage_base': {'positive': 'false', 'mode': 'add'},     # 应该在这？
    'pop_housing_usage_add': {'positive': 'false', 'mode': 'add'},
    'pop_amenities_usage_base': {'positive': 'false', 'mode': 'add'},     # 应该在这？
    'pop_amenities_usage_no_happiness_base': {'positive': 'false', 'mode': 'add'},     # 应该在这？

    # + +
    'district_generator_max': {'positive': 'true', 'mode': 'add'},
    'district_mining_max': {'positive': 'true', 'mode': 'add'},
    'district_farming_max': {'positive': 'true', 'mode': 'add'},
    'building_mote_harvesters_max': {'positive': 'true', 'mode': 'add'},
    'building_gas_extractors_max': {'positive': 'true', 'mode': 'add'},
    'building_crystal_mines_max': {'positive': 'true', 'mode': 'add'},
    'building_betharian_power_plant_max': {'positive': 'true', 'mode': 'add'},
    'building_xeno_zoo_max': {'positive': 'true', 'mode': 'add'},
    'pop_political_power': {'positive': 'true', 'mode': 'add'},     # 应该在这？

    # + *
    'faction_approval': {'positive': 'true', 'mode': 'mult'},
    'planet_max_districts_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_migration_all_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_amenities_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_housing_mult': {'positive': 'true', 'mode': 'mult'},
    'trade_value_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_orbital_bombardment_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_building_refund_mult': {'positive': 'true', 'mode': 'mult'},
    'planet_amenities_no_happiness_mult': {'positive': 'true', 'mode': 'mult'},

    'faction_influence_mult': {'positive': 'true', 'mode': 'mult'},
    'pop_consumer_goods_mult': {'positive': 'false', 'mode': 'mult'},
    'rivalry_influence_gain': {'positive': 'true', 'mode': 'mult'},
    'country_border_mult': {'positive': 'true', 'mode': 'mult'},
    'country_border_friction_mult': {'positive': 'false', 'mode': 'mult'},
    'country_core_sector_system_cap': {'positive': 'true', 'mode': 'add'},
    'planet_unrest_mult': {'positive': 'false', 'mode': 'mult'},
    'shipclass_military_station_hit_points_mult': {'positive': 'true', 'mode': 'mult'},
    'country_unrest_unhappy_pop_effect_mult': {'positive': 'false', 'mode': 'mult'},
    'pop_other_species_happiness': {'positive': 'true', 'mode': 'mult'},
    'planet_orbital_bombardment_damage': {'positive': 'false', 'mode': 'mult'},
    'biological_pop_happiness': {'positive': 'true', 'mode': 'mult'},
    'max_rivalries': {'positive': 'true', 'mode': 'add'},
    'ship_armor_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_shield_mult': {'positive': 'true', 'mode': 'mult'},
    'pop_owner_happiness': {'positive': 'true', 'mode': 'mult'},
    'pop_food_req_mult': {'positive': 'false', 'mode': 'mult'},
    'planet_migration_all_pull': {'positive': 'true', 'mode': 'mult'},
    'important': {'positive': 'true', 'mode': 'add'},
    'planet_unrest_add': {'positive': 'false', 'mode': 'add'},
    'army_health': {'positive': 'true', 'mode': 'mult'},
    'starbase_shipyard_build_time_mult': {'positive': 'false', 'mode': 'mult'},
    'ship_hull_regen_add_perc': {'positive': 'true', 'mode': 'add_perc'},
    'ship_armor_regen_add_perc': {'positive': 'true', 'mode': 'add_perc'},
    'ship_anomaly_fail_risk': {'positive': 'false', 'mode': 'mult'},
    'faction_happiness': {'positive': 'true', 'mode': 'mult'},
    'country_leader_cap': {'positive': 'true', 'mode': 'add'},
    'country_war_exhaustion_mult': {'positive': 'false', 'mode': 'mult'},
    'planet_migration_xeno_pull': {'positive': 'true', 'mode': 'mult'},
    'country_unrest_unhappy_slave_effect_mult': {'positive': 'false', 'mode': 'mult'},
    'max_minerals': {'positive': 'true', 'mode': 'add'},
    'max_energy': {'positive': 'true', 'mode': 'add'},
    'pc_nuked_habitability': {'positive': 'true', 'mode': 'add'},
    'army_attack_morale_mult': {'positive': 'true', 'mode': 'mult'},
    'army_defense_health_mult': {'positive': 'true', 'mode': 'mult'},
    'country_trust_growth': {'positive': 'true', 'mode': 'mult'},
    'federation_naval_cap_contribution_mult': {'positive': 'true', 'mode': 'mult'},
    'shipclass_science_ship_disengage_mult': {'positive': 'true', 'mode': 'mult'},
    'country_subject_technology_sharing_mult': {'positive': 'true', 'mode': 'mult'},
    'subject_tribute_mult': {'positive': 'true', 'mode': 'mult'},
    'country_integration_cooldown_mult': {'positive': 'false', 'mode': 'mult'},
    'country_vassal_naval_capacity_contribution_mult': {'positive': 'true', 'mode': 'mult'},
    'mod_distance_to_capital_static_modifier_efficiency_mult': {'positive': 'false', 'mode': 'mult'},
    'pop_other_species_owner_happiness': {'positive': 'replacetrue', 'mode': 'mult'},
    'pop_eff_wo_slaves': {'positive': 'true', 'mode': 'mult'},
    'pop_food_mult': {'positive': 'true', 'mode': 'mult'},
    'country_piracy_risk_mult': {'positive': 'false', 'mode': 'mult'},
    'ship_emergency_ftl_min_days_mult': {'positive': 'false', 'mode': 'mult'},
    'max_food': {'positive': 'false', 'mode': 'add'},
    'ship_windup_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_winddown_mult': {'positive': 'true', 'mode': 'mult'},
    'ship_ftl_jumpdrive_range_mult': {'positive': 'true', 'mode': 'mult'},
    'country_unity_produces_mult': {'positive': 'true', 'mode': 'mult'},
}

# 重要逻辑词
pdx_logic_word = {'AND', 'OR', 'NOR', 'NAND'}

# effect_%s
# %s_trigger
# %s_build_cost_mult
# %s_hull_mult
# %s_build_speed_mult
# %s_evasion_add
# %s_damage_mult
# %s_disengage_mult
# %s_weapon_damage_mult
# %s_speed_mult
# %s_weapon_fire_rate_mult
# can_destroy_planet_with_%s
# %s_ACTION
# FLEETORDER_DESTROY_PLANET_WITH_%s
# damage_vs_country_type_%s_mult
# %s_habitability
# trait_%s_preference
# %s_short
# EMPIRE_DESIGN_%s
# EMPIRE_DESIGN_%s_desc
# %s_CONSTRUCTION_INFO_DELAYED
# %s_MEGASTRUCTURE_DETAILS
# %s_DESC
# war_goal_%s
# war_goal_%s_desc
# casus_belli_%s
# casus_belli_%s_acquire_hint
# %s_desc
# %s_value
# %s_NAME
# HAS_NOT_FORMER_%s_TYPE
# HAS_FORMER_%s_TYPE
# on_building_%s
# MESSAGE_DESC_FOR_%s
# GFX_%s
# SHIP_STAT_CONTRIBUTION_ADDATIVE_%s
# SHIP_STAT_CONTRIBUTION_MULTIPLICATIVE_%s
# SHIP_STAT_%s
# SHIP_STAT_DESC_%s
# combat_%s
# ANY_%s


# 逻辑词
pdx_logic = {
    'AND': {'value': 'AND_TRIGGER_STARTS', 'positive': True},
    'OR': {'value': 'OR_TRIGGER_STARTS', 'positive': True},
    'NOR': {'value': 'NOR_TRIGGER_STARTS', 'positive': False},
    'NAND': {'value': 'NAND_TRIGGER_STARTS', 'positive': False},
    'not_OR': {'value': 'NOR_TRIGGER_STARTS', 'positive': False},
    'has_civic': {'value': 'TRIGGER_HAS_CIVIC', 'positive': True},

    'if': {'value': '如果'},
    'else': {'value': '否则'},
    'else_if': {'value': '或者如果'},
    'hidden_effect': {'value': '隐藏效果'},
    'limit': {'value': '满足以下条件时：'},
    'potential': {'value': '基础要求'},
    'custom_tooltip': {'value': ''},
    'value': {'value': '基础值 = '},
    'factor': {'value': '系数 × '},
    'weight': {'value': '权重 = '},
    'random_weight': {'value': '随机权重'},
    'break': {'value': '分支结束'},

    'is_robotic': {'value': '是机械人口'},
    'has_living_standard': {'value': '生活标准为', 'positive': True},
    'has_election_type': {'value': '选举方式为'},
    'is_in_federation_with': {'value': 'IS_IN_FEDERATION_WITH_TOOLTIP', 'positive': True},
    'is_non_sapient_robot': {'value': '是非开智机械', 'positive': True},
    'is_hostile_to': {'value': '与$has_a$敌对', 'positive': True},
    'years_of_peace': {'value': '和平年数'},
    'root': {'value': '己方'},
    'who': {'value': '主体'},
    'from': {'value': '对方', 'positive': True},
    'delay': {'value': '延迟天数'},
    'overlord': {'value': '宗主'},
    'is_pop_faction_type': {'value': '派系是：', 'positive': True},
    'mid_game_years_passed': {'value': '游戏中期已过年数'},
    'years_passed': {'value': '年数', 'positive': True},
    'not_from': {'value': '没有', 'positive': False},
    'civics': {'value': 'GOVERNMENT_CIVICS'},
    'authority': {'value': 'GOVERNMENT_AUTHORITY'},
    'not_value': {'value': '基础值≠ '},
    'country_type': {'value': 'IS_COUNTRY_TYPE'},
    'has_research_agreement': {'value': '拥有研究协议', 'positive': True},
    'random_owned_pop': {'value': 'effect_random_owned_pop'},
    'add_deposit': {'value': '在目标星球上添加$has_a$'},
    'add_district': {'value': 'ADD_DISTRICT_EFFECT'},
    'has_country_flag': {'value': '有国家标识', 'positive': True},
    'tech_unlocked_ratio': {'value': '解锁科技的比率'},
    'ratio': {'value': '比率'},
    'set_subject_of': {'value': '附庸国设定为'},
    'subject_type': {'value': '附庸类型'},
    'join_war': {'value': '加入战争'},
    'shift_ethic': {'value': '转变思潮'},
    'count_owned_pops': {'value': '拥有的人口：'},
    'count': {'value': '数量', 'positive': True},
    'valid_objects': {'value': '符合条件的物体'},
    'not_exists': {'value': '没有', 'positive': False},
    'is_event_leader': {'value': '事件领袖'},
    'pop_faction_event': {'value': '触发派系事件'},
    'id': {'value': 'id'},


    # True or False
    'has_valid_civic': {'value': 'TRIGGER_HAS_VALID_CIVIC', 'positive': True},
    'not_has_valid_civic': {'value': 'TRIGGER_HAS_NOT_VALID_CIVIC', 'positive': False},

    'is_same_value': {'value': '与$has_a$相同', 'positive': True},
    'not_is_same_value': {'value': '与$has_a$不相同', 'positive': False},

    'is_same_species': {'value': 'IS_SAME_SPECIES', 'positive': True},
    'not_is_same_species': {'value': 'IS_NOT_SAME_SPECIES', 'positive': False},

    'has_trait': {'value': 'HAS_TRAIT', 'positive': True},
    'not_has_trait': {'value': 'DOES_NOT_HAVE_TRAIT', 'positive': False},

    'is_controlled_by': {'value': 'IS_CONTROLLED_BY', 'positive': True},
    'not_is_controlled_by': {'value': 'IS_NOT_CONTROLLED_BY', 'positive': False},

    'has_policy_flag': {'value': '拥有政策标识', 'positive': True},
    'not_has_policy_flag': {'value': '没有政策标识', 'positive': False},

    'has_origin': {'value': 'TRIGGER_HAS_ORIGIN', 'positive': True},
    'not_has_origin': {'value': 'TRIGGER_NOT_HAS_ORIGIN', 'positive': False},

    'host_has_dlc': {'value': '主机拥有DLC：', 'positive': True},
    'not_host_has_dlc': {'value': '主机没有DLC：', 'positive': False},

    'has_global_flag': {'value': 'HAS_GLOBAL_FLAG', 'positive': True},
    'not_has_global_flag': {'value': 'HAS_NOT_GLOBAL_FLAG', 'positive': False},

    'is_domineering_to': {'value': 'IS_DOMINEERING_TO_TOOLTIP', 'positive': True},
    'not_is_domineering_to': {'value': 'IS_NOT_DOMINEERING_TO_TOOLTIP', 'positive': False},

    'has_ethic': {'value': 'HAS_ETHIC', 'positive': True},
    'not_has_ethic': {'value': 'DOES_NOT_HAVE_ETHIC', 'positive': False},

    'num_free_districts': {'value': 'HAS_NUM_FREE_DISTRICTS', 'positive': True},
    'not_num_free_districts': {'value': 'HAS_NOT_NUM_FREE_DISTRICTS', 'positive': False},

    'has_star_flag': {'value': '有恒星标识', 'positive': True},
    'not_has_star_flag': {'value': '没有恒星标识', 'positive': False},

    'leader_class': {'value': '领袖是', 'positive': True},
    'not_leader_class': {'value': '领袖不是', 'positive': False},

    'is_star': {'value': 'PLANET_IS_STAR', 'positive': True},
    'not_is_star': {'value': 'PLANET_IS_NOT_STAR', 'positive': False},

    'has_ascension_perk': {'value': 'TRIGGER_HAS_ASCENSION_PERK', 'positive': True},
    'not_has_ascension_perk': {'value': 'TRIGGER_NOT_HAS_ASCENSION_PERK', 'positive': False},

    'has_authority': {'value': '有$has_a$政体', 'positive': True},
    'not_has_authority': {'value': '没有$has_a$政体', 'positive': False},

    'is_country_type': {'value': 'IS_COUNTRY_TYPE', 'positive': True},
    'not_is_country_type': {'value': 'IS_NOT_COUNTRY_TYPE', 'positive': False},

    # DLC
    'Leviathans Story Pack': {'value': '利维坦', 'positive': True},
    'Utopia': {'value': '乌托邦', 'positive': True},
    'Synthetic Dawn Story Pack': {'value': '合成人黎明', 'positive': True},
    'Apocalypse': {'value': '启示录', 'positive': True},
    'Distant Stars Story Pack': {'value': '遥远星系', 'positive': True},
    'Megacorp': {'value': '寰宇企业', 'positive': True},
    'Ancient Relics Story Pack': {'value': '远古遗迹', 'positive': True},
    'Lithoids Species Pack': {'value': '石质种族', 'positive': True},
    'Federations': {'value': '联邦', 'positive': True},
}

pdx_logic_2 = {
    'is_preferred_weapons': {'value': 'IS_PREFERRED_WEAPONS_TRIGGER', 'positive': True},
    'not_is_preferred_weapons': {'value': 'IS_NOT_PREFERRED_WEAPONS_TRIGGER', 'positive': False},
    'not_has_civic': {'value': 'TRIGGER_NOT_HAS_CIVIC', 'positive': True},
    'allows_slavery': {'value': 'ALLOWS_SLAVERY', 'positive': True},
    'modifier': {'value': '修正：', 'positive': True},
    'weight_modifier': {'value': '权重修正', 'positive': True},
    'exists': {'value': '$啥玩意$存在', 'positive': True},
    'pop_faction': {'value': 'POP_FACTION', 'positive': True},
    'slavery_not_allowed': {'value': '禁止奴隶制', 'positive': True},
    'num_communications': {'value': '建立通讯数量', 'positive': True},
    # 'not_years_passed': {'value': '年数不到', 'positive': False},
    'has_government': {'value': '有$has_a$政体', 'positive': True},
    'not_has_government': {'value': '没有$has_a$政体', 'positive': False},
    'country_type': {'value': '国家类型'},
    'is_planet_class': {'value': '星球类型是', 'positive': True},
    'not_is_planet_class': {'value': '星球类型不是', 'positive': False},
    'num_modifiers': {'value': '修正数量'},
    'spawn_chance': {'value': '出现概率'},
    'has_planet_modifier': {'value': '有星球修正', 'positive': True},
    'add': {'value': '增加', 'positive': True},
    'num_moons': {'value': '卫星数量'},
    'has_moon': {'value': '拥有卫星：'},
    'no': {'value': '否'},
    'yes': {'value': '是'},
    'is_moon': {'value': '是卫星'},
    'planet_size': {'value': '星球大小'},
    'ethics': {'value': 'ETHICS'},
    'authority': {'value': 'GOVERNMENT_AUTHORITY'},
    'base': {'value': '基础值'},
    'default': {'value': '普通帝国'},
    'primitive': {'value': '原始文明'},
    'enclave': {'value': '城邦'},
    'sentinels': {'value': '哨兵'},
    'ai_empire': {'value': '肃正协议'},
    'dormant_marauders': {'value': '劫掠者'},
    'awakened_marauders': {'value': '复兴劫掠者'},
    'drop_weight': {'value': '地块资源权重：'},
    'orbital_weight': {'value': '轨道资源权重：'},
    'planet': {'value': '星球'},
    'has_owner': {'value': '已被殖民：', 'positive': True},
    'is_asteroid': {'value': '小行星：', 'positive': True},
    'has_strategic_resource': {'value': '有战略资源：', 'positive': True},
    'is_inside_nebula': {'value': '在星云内：', 'positive': True},
    'not_is_in_cluster': {'value': '不在资源聚集区', 'positive': False},
    'is_in_cluster': {'value': '在资源聚集区', 'positive': True},
    'not_has_country_flag': {'value': '没有国家标识', 'positive': False},
    'has_deposit': {'value': '有资源点', 'positive': True},
    'solar_system': {'value': '恒星系'},
    'is_star_class': {'value': '恒星类型', 'positive': True},
    'has_swapped_tradition': {'value': '有$has_a$传统', 'positive': True},
    'not_has_swapped_tradition': {'value': '没有$has_a$传统', 'positive': False},
    'has_non_swapped_tradition': {'value': '有$has_a$传统', 'positive': True},
    'not_has_non_swapped_tradition': {'value': '没有$has_a$传统', 'positive': False},
    'owner': {'value': '拥有者：', 'positive': True},
    'not_owner': {'value': '拥有者没有：', 'positive': False},
    'is_capital': {'value': '是首都星球：', 'positive': True},
    'has_building': {'value': '拥有建筑：', 'positive': True},
    'not_has_building': {'value': '没有建筑：', 'positive': False},
    'has_ascension_perk': {'value': '拥有$has_a$飞升', 'positive': False},
    'planet.owner': {'value': '星球拥有者'},
    'check_variable': {'value': '检查变量：'},
    'which': {'value': '', 'positive': True},
    'ai_weight': {'value': 'AI权重'},
    'ai_allow': {'value': 'AI建造条件'},
    'allow': {'value': '要求'},
    'amount': {'value': '数量'},
    'tile': {'value': '地块'},
    'has_resource': {'value': '拥有资源：', 'positive': True},
    'type': {'value': '类型'},
    'sector_controlled': {'value': '由星区掌控：', 'positive': True},
    'has_technology': {'value': '拥有$has_a$科技', 'positive': True},
    'not_has_technology': {'value': '没有$has_a$科技', 'positive': False},
    'not_planet': {'value': '星球没有', 'positive': False},
    'is_enslaved': {'value': '被奴役', 'positive': True},
    'count_pops': {'value': '满足条件人口：', 'positive': True},
    'count_tile': {'value': '满足条件地块：', 'positive': True},
    'unrest': {'value': 'UNREST', 'positive': True},
    'destroy_if': {'value': '满足以下条件强制拆除'},
    'show_tech_unlock_if': {'value': '显示其科技所需条件'},
    'has_megastructure': {'value': '拥有巨型建筑：', 'positive': True},
    'active': {'value': ''},
    'has_grown_pop': {'value': '有已成长人口：', 'positive': True},
    'pop': {'value': '人口'},
    'resources': {'value': '额外产出：', 'positive': True},
    'research_leader': {'value': '科学领袖：'},
    'not_research_leader': {'value': '科学领袖未达到：'},
    'has_tradition': {'value': '拥有$has_a$传统', 'positive': True},
    'has_level': {'value': '等级', 'positive': True},
    'has_modifier': {'value': '有修正', 'positive': True},
    'not_has_modifier': {'value': '没有修正', 'positive': False},
    'num_owned_planets': {'value': '拥有行星数量'},
    'has_ai_personality': {'value': '拥有$has_a$性格', 'positive': True},
    'has_ai_personality_behaviour': {'value': '拥有$has_a$性格', 'positive': True},
    'any_relation': {'value': '任何相关国家满足：', 'positive': True},
    'not_any_relation': {'value': '任何相关国家都不满足：', 'positive': False},
    'has_communications': {'value': '与$has_a$有通讯', 'positive': True},
    'ROOT': {'value': '我们'},
    'any_owned_pop': {'value': '任意拥有的人口：'},
    'any_owned_pops': {'value': '任意拥有的人口：'},
    'not_any_owned_pop': {'value': '任意拥有的人口都不满足：', 'positive': False},
    'any_system_within_border': {'value': '境内星系：'},
    'election_candidates': {'value': '参选权重：'},
    'has_federation': {'value': '存在联邦：'},
    'not_any_subject': {'value': '任意附庸都不满足', 'positive': False},
    'is_subject_type': {'value': '附庸类型为', 'positive': True},
    'not_is_subject_type': {'value': '附庸类型不是', 'positive': False},
    'is_colonizable': {'value': '是可殖民星球：'},
    'not_has_ascension_perk': {'value': '没有$TRADITION|Y$飞升天赋', 'positive': False},
    'not_has_ai_personality_behaviour': {'value': '没有$PERSONALITY|Y$行为', 'positive': False},
    'is_xenophile': {'value': '是亲外主义：'},
    'is_xenophobe': {'value': '是排外主义：'},
    'is_pacifist': {'value': '是和平主义：'},
    'is_militarist': {'value': '是军国主义：'},
    'is_materialist': {'value': '是唯物主义：'},
    'is_spiritualist': {'value': '是唯心主义：'},
    'is_egalitarian': {'value': '是平等主义：'},
    'is_authoritarian': {'value': '是威权主义：'},
    'is_colony': {'value': '是殖民地：'},
    'any_neighbor_country': {'value': '任意邻国'},
    'any_country': {'value': '任意国家'},
    'not_any_country': {'value': '任意国家都不满足', 'positive': False},
    'num_ascension_perks': {'value': '飞升数量'},
    'is_mechanical_empire': {'value': '是机械帝国：'},
    'is_cyborg_empire': {'value': '是合成人帝国：'},
    'condition': {'value': '条件'},
    'is_owned_by': {'value': '是$has_a$所有'},
    'root': {'value': '该行为的执行者'},
    'area': {'value': '领域：'},
    'has_orbital_bombardment': {'value': '轨道轰炸中：'},
    'num_pops': {'value': '人口数'},
    'has_comms_with_alien_empire': {'value': '与外星帝国有过接触'},
    'has_comms_with_alien_civilization': {'value': '与外星文明有过接触'},
    'habitable_structure': {'value': '是栖息地：'},
    'not_has_planet_flag': {'value': '没有行星标识', 'positive': False},
    'starbase': {'value': '恒星基地'},
    'set_planet_flag': {'value': '添加行星标识'},
    'set_star_flag': {'value': '添加恒星标识'},
    'set_country_flag': {'value': '添加国家标识'},
    'any_neighbor_system': {'value': '任意相邻星系'},
    'every_system_planet': {'value': '星系内所有星球'},
    'is_star': {'value': '是恒星'},
    'remove_planet': {'value': '移除星球'},
    'asteroids_distance': {'value': '小行星带半径'},
    'remove_megastructure': {'value': '移除巨型建筑'},
    'spawn_megastructure': {'value': '生成该巨型建筑的巨型建筑'},
    'name': {'value': '名称：'},
    'orbit_angle': {'value': '轨道角度'},
    'orbit_distance': {'value': '轨道半径'},
    'location': {'value': '基准位置'},
    'change_pc': {'value': '星球类型更换为'},
    'every_system_ambient_object': {'value': '星系内所有环境物体'},
    'destroy_ambient_object': {'value': '摧毁环境物体'},
    'country_event': {'value': '触发国家事件'},
    'id': {'value': 'id：'},
    'planet_possible': {'value': '行星满足要求：'},
    'spawn_planet': {'value': '创建星球：'},
    'orbit_angle_offset': {'value': '轨道角度偏移：'},
    'init_effect': {'value': '初始设定：'},
    'set_name': {'value': '名称：'},
    'set_planet_entity': {'value': '模型设定：'},
    'entity': {'value': '模型：'},
    'surveyed': {'value': '调查情况：'},
    'set_surveyed': {'value': '已调查：'},
    'set_all_comms_surveyed': {'value': '所有已通讯国家均调查过：'},
    'class': {'value': '类型'},
    'any_tile': {'value': '任意地块'},
    'has_blocker': {'value': '有地块障碍'},
    'random_tile': {'value': '随机地块'},
    'remove_blocker': {'value': '移除地块障碍'},
    'save_event_target_as': {'value': '设置为$has_a$事件目标'},
    'trigger_megastructure_icon': {'value': '设置巨型建筑图标'},
    'fromfrom.planet': {'value': '目标行星'},
    'event_target': {'value': '事件目标'},
    'while': {'value': '循环'},
    'remove_star_flag': {'value': '移除恒星标识'},
    'this': {'value': ''},
    'activate_gateway': {'value': '激活星门'},
    'num_active_gateways': {'value': '已激活星门数'},
    'random_megastructure': {'value': '随机巨型建筑'},
    'is_megastructure_type': {'value': '巨型建筑类型为'},
    'upgrade_megastructure_to': {'value': '升级为巨型建筑'},
    'finish_upgrade': {'value': '完成升级'},
    'orbit_location': {'value': '轨道位置'},
    'orbit_distance_offset': {'value': '轨道距离偏移量'},
    'size': {'value': '星球'},
    'has_ring': {'value': '是否有环'},
    'colonizeable_planet': {'value': '是可宜居行星'},
    'copy_orbital_tile': {'value': '复制$has_a$的轨道资源地块'},
    'is_subject': {'value': '是附庸国'},
    'is_berserk_fallen_machine_empire': {'value': '是§H失常的监护§!'},
    'has_claim': {'value': '拥有宣称：'},
    'FROM': {'value': '防御方'},
    'has_total_war_cb': {'value': '拥有§H灭绝战争§!的宣战借口'},
    'overlord': {'value': '宗主国'},
    'is_rival': {'value': '是$has_a$的宿敌'},
    'is_neighbor_of': {'value': '与$has_a$相邻'},
    'any_ship': {'value': '任意舰船'},
    'not_any_ship': {'value': '任意舰船都不是', 'positive': False},
    'is_ship_size': {'value': '舰船类型是'},
    'has_opinion_modifier': {'value': '拥有好感度修正'},
    'is_at_war': {'value': '处于战争状态'},
    'has_met_primitives': {'value': '已遇见过原始文明'},
    'can_set_ai_policy': {'value': '可以设置人工智能政策'},
    'can_set_robot_policy': {'value': '可以设置机器人政策'},
    'any_planet_within_border': {'value': '境内任意行星'},
    'any_pop': {'value': '任意人口'},
    'is_sapient': {'value': '是已开智人口'},
    'has_encountered_other_species': {'value': '已遇见过其他种族'},
    'has_valid_ai_personality': {'value': '有有效的AI性格'},
    'multispecies': {'value': '给予外星物种权利'},
    'attack_neutrals': {'value': '攻击中立势力'},
    'is_ai': {'value': '是AI'},
    'check_casus_belli_valid': {'value': '检查以下宣战借口的可用性'},
    'is_shackled_robot': {'value': '被奴役的机械'},
    'is_being_purged': {'value': '正在被净化的人口'},
    'has_culture_shock': {'value': '被文化冲击的人口'},
    'leader': {'value': '领袖'},
    'remove_modifier': {'value': '移除修正'},
    'owner_species': {'value': '主体种族'},
    'species': {'value': '种族'},
    'is_robot_pop': {'value': '是机械人口'},
    'root.owner': {'value': '所属国家'},
    'has_any_tradition_unlocked': {'value': '已解锁任意传统'},
    'prev': {'value': '前者'},
    'count_neighbor_country': {'value': '邻国数量'},
    'is_overlord': {'value': '宗主国'},
    'guardian': {'value': '守护者'},
    'guardian_dragon': {'value': '以太巨龙'},
    'guardian_stellarite': {'value': '噬星者'},
    'guardian_wraith': {'value': '幽魂'},
    'guardian_hiver': {'value': '蜂巢小行星'},
    'guardian_horror': {'value': '位面之魇'},
    'guardian_fortress': {'value': '神秘堡垒'},
    'guardian_dreadnought': {'value': '无畏战舰'},
    'guardian_sphere': {'value': '无限神机'},
    'is_war_participant': {'value': '是参战方'},
    'attackers': {'value': '进攻方'},
    'any_war': {'value': '任意战争'},
    'has_diplo_migration_treaty': {'value': '有移民条约'},
    'has_non_aggression_pact': {'value': '有互不侵犯条约'},
    'has_migration_control': {'value': '有移民管控'},
    'has_citizenship_type': {'value': '公民权类型为'},
    'has_citizenship_rights': {'value': '有公民权'},
    'country': {'value': '国家'},
    'nany_owned_planets': {'value': '任意拥有的行星'},
    'num_strategic_resources': {'value': '任意拥有的行星'},
    'ruler': {'value': '统治者'},
    'has_population_control': {'value': '人口管制'},
    'num_species': {'value': '种族数量'},
    'not_is_in_federation_with': {'value': '与$has_a$不在同一联邦'},
    'not_is_exact_same_species': {'value': '与$has_a$不严格相同的种族', 'positive': False},
    'count_country': {'value': '国家数量'},
    'add_modifier': {'value': '添加修正'},
    'support': {'value': '支持率'},
    'parameter:empire': {'value': '国家参数'},
    'days': {'value': '天数'},
    'every_pop_faction': {'value': '每个派系'},
    'every_relation': {'value': '每个已通信国家'},
    'leader_of_faction': {'value': '派系领导人'},
    'count_pop_factions': {'value': '派系人口数'},
    'is_country_type_with_subjects': {'value': '国家有附庸国'},
    'every_system_within_border': {'value': '疆域内所有星系'},
    'add_claims': {'value': '增加s宣称'},
    'remove_claims': {'value': '移出宣称'},
    'add_threat': {'value': '增加威胁度'},
    'fallen_empire_humiliate_effect': {'value': '失落帝国羞辱效果'},
    'is_valid_target_fe_stop_atrocities': {'value': '目标是失落帝国施行§Y中止暴行§!的可用目标'},
    'is_valid_target_fe_stop_ai': {'value': '目标是失落帝国施行§Y人工智能非法化§!的可用目标'},
    'is_valid_target_fe_cleanse_holy_worlds': {'value': '目标是失落帝国施行§Y净化圣地§!的可用目标'},
    'every_playable_country': {'value': '每个可玩国家'},
    'count_starbase_modules': {'value': '恒星基地模块数量'},
    'has_starbase_building': {'value': '有恒星基地建筑'},
    'country_naval_cap_add': {'value': '海军容量上限增加'},
    'hidden_trigger': {'value': '隐藏效果'},
    'has_starbase_size': {'value': '恒星基地等级'},
    'change_variable': {'value': '修改变量'},
    'is_ironman': {'value': '铁人模式'},
    'space_owner': {'value': '恒星系所属者'},
    'has_event_chain': {'value': '有事件链'},
    # 'fromfrom': {'value': ''},
}

pdx_dict_detail = {
    'election_type': {'value': '选举类型：'},
    'election_term_years': {'value': '任期年限：'},
    're_election_allowed': {'value': '允许重新选举', 'deny': '不'},
    'uses_mandates': {'value': '有选举承诺', 'deny': '没'},
    'has_agendas': {'value': '有议程', 'deny': '没'},
    'can_have_emergency_elections': {'value': '可以紧急选举', 'deny': '不'},
    'emergency_election_cost': {'value': '紧急选举花费£influence影响力：'},
    'max_election_candidates': {'value': '选举人最大数量：'},
    'has_heir': {'value': '有继承人', 'deny': '没'},
    'has_factions': {'value': '有派系', 'deny': '没'},
    'can_reform': {'value': '可以改革', 'deny': '不'},
    'valid_for_released_vassal': {'value': '允许手动释放附庸', 'deny': '不'},
}

pdx_resource = {
    'influence': 'influence',
    'unity': 'unity',
    'energy': 'energy',
    'physics_research': 'physics',
    'society_research': 'society',
    'engineering_research': 'engineering',
    'minerals': 'minerals',
    'food': 'food',
    'alloys': 'alloys',
    'consumer_goods': 'consumer_goods',
    'volatile_motes': 'volatile_motes',
    'exotic_gases': 'exotic_gases',
    'rare_crystals': 'rare_crystals',
    'nanites': 'nanites',
    'trade_value': 'trade_value',
    'sr_living_metal': 'sr_living_metal',
    'sr_zro': 'sr_zro',
    'time': 'time',

    # old ones
    'sr_terraform_gases': 'sr_terraform_gases',
    'sr_terraform_liquids': 'sr_terraform_liquids',
    'sr_garanthium': 'sr_garanthium',
    'sr_lythuric': 'sr_lythuric',
    'sr_teldar': 'sr_teldar',
    'sr_yuranic': 'sr_yuranic',
    'sr_orillium': 'sr_orillium',
    'sr_pitharan': 'sr_pitharan',
    'sr_engos': 'sr_engos',
    'sr_neutronium': 'sr_neutronium',
    'sr_dark_matter': 'sr_dark_matter',
    'sr_satramene': 'sr_satramene',
    'sr_alien_pets': 'sr_alien_pets',
    'sr_betharian': 'sr_betharian',
    'sr_riggan': 'sr_riggan',
    'sr_xuran': 'sr_xuran',
    'sr_muutagan': 'sr_muutagan',
}
