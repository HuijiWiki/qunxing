import re
from collections import OrderedDict

from DDSImages import get_dds_images
from StellarisData import Interface, ScriptedVariables, Ethics, Agendas, Authorities, Subjects, Traits, PopFactionTypes, \
    WarGoals, CasusBelli, PlanetClasses, StarClasses, Terraform, StaticModifiers, PlanetModifiers, Deposits, \
    ComponentSets, ShipBehaviors, ShipSizes, SectionTemplates, ComponentTemplates, StarbaseLevels, StarbaseBuildings, \
    StarbaseModules, BombardmentStances, Personalities, Policies, Civics, TraditionCategory, Traditions, AscensionPerks, \
    Governments, Edicts, Armies, StrategicResources, Megastructures, Buildings, DepositCategories, Districts, PopJobs, \
    PopCategories, Technology, Achievements, Events, Decisions, GlobalShipDesigns, Relics
from data_uploader import upload_dict, log_in
from danteng import Danteng
# import hashlib


if __name__ == '__main__':
    # 程序配置
    stellaris_path = 'F:\\Games\\Steam\\steamapps\\common\\Stellaris\\'
    common_path = stellaris_path + 'common\\'
    event_path = stellaris_path + 'events\\'
    gfx_path = stellaris_path + 'gfx'
    is_upload = True

    Danteng.log('————————————————处理图片————————————————')
    un_process = get_dds_images(gfx_path, True)

    wiki = False
    while not wiki:
        wiki = log_in()

    z = 1
    reflex_dict = {
        'gfx': Interface,
        'scripted variables': ScriptedVariables,
        # 'ethics': Ethics,
        # 'agendas': Agendas,
        # 'authorities': Authorities,
        # 'subjects': Subjects,
        # 'traits': Traits,
        # 'pop_faction_types': PopFactionTypes,
        # 'war_goals': WarGoals,
        # 'casus_belli': CasusBelli,
        # 'planet_classes': PlanetClasses,
        # 'star_classes': StarClasses,
        # 'terraform': Terraform,
        # 'static_modifiers': StaticModifiers,
        # 'planet_modifiers': PlanetModifiers,
        # 'districts': Districts,
        # 'deposit_categories': DepositCategories,
        # 'deposits': Deposits,
        # 'component_sets': ComponentSets,
        # 'ship_behaviors': ShipBehaviors,
        # 'ship_sizes': ShipSizes,
        # 'section_templates': SectionTemplates,
        # 'component_templates': ComponentTemplates,
        # 'starbase_levels': StarbaseLevels,
        # 'starbase_buildings': StarbaseBuildings,
        # 'starbase_modules': StarbaseModules,
        # 'bombardment_stances': BombardmentStances,
        # 'personalities': Personalities,
        # 'policies': Policies,
        # 'global_ship_designs': GlobalShipDesigns,
        # 'civics': Civics,
        # 'tradition_categories': TraditionCategory,
        # 'traditions': Traditions,
        # 'ascension_perks': AscensionPerks,
        # 'governments': Governments,
        # 'edicts': Edicts,
        # 'decisions': Decisions,
        # 'armies': Armies,
        # 'pop_categories': PopCategories,
        # 'pop_jobs': PopJobs,
        # 'relics': Relics,
        # 'strategic_resources': StrategicResources,
        # 'megastructures': Megastructures,
        # 'buildings': Buildings,
        # 'technology': Technology,
        # 'achievements': Achievements,
        'events': Events,
    }

    data = OrderedDict()
    for type_name in reflex_dict:
        data[type_name] = reflex_dict[type_name]()
        data[type_name].processor()
    all_data = data['gfx'].all_data
    data['gfx'].get_loc_icon()

    z = 2

    uploaded = []

    none_data_types = ['interface', 'global', 'component_sets', 'tradition_categories', 'deposit_categories']
    for name in all_data:
        if name not in none_data_types:
            for item in all_data[name]:
                page_name = name + '/' + item
                item_data = all_data[name][item]
                upload_dict(page_name, item_data, wiki, is_upload=True)
            uploaded.append(name)

    wiki.wait_threads()
    Danteng.log('Done')
    z = 1


# agendas                                   2.0.2
# ambient_objects                           首轮暂不处理
# anomalies                                 首轮暂不处理
# armies                                    2.0.2
# ascension_perks                           2.0.2
# attitudes                                 首轮暂不处理
# bombardment_stances                       2.0.2
# buildable_pops                            首轮暂不处理
# buildings                                 2.0.2
# building_tags                             只是分类
# button_effects                            没东西
# bypass                                    首轮暂不处理
# casus_belli                               2.0.2
# colors                                    都是rgb
# component_sets                            提供图标
# component_tags                            只是标签
# component_templates                       2.0.2       需要舰船模拟器
# country_customization                     首轮暂不处理
# country_types                             首轮暂不处理
# defines                                   再说吧
# deposits                                  2.0.2
# diplomatic_actions                        首轮暂不处理
# diplo_phrases                             打招呼句子
# edicts                                    2.0.2
# ethics                                    2.0.2
# event_chains                              事件链图标之类的
# fallen_empires                            首轮暂不处理
# game_rules                                再说吧
# TODO:global_ship_designs       需要舰船模拟器
# governments                               2.0.2
# authorities                               2.0.2
# civics                                    2.0.2
# graphical_culture                         你觉得怎么搞
# mandates                                  首轮暂不处理
# map_modes                                 再说吧
# megastructures                            2.0.2
# name_lists                                名字列表，不搞
# notification_modifiers                    没东西
# observation_station_missions              首轮暂不处理
# on_actions                                首轮暂不处理
# opinion_modifiers                         再说吧
# personalities                             2.0.2
# planet_classes                            2.0.2
# planet_modifiers                          2.0.2
# policies                                  2.0.2
# pop_faction_types                         2.0.2       需要列表
# precursor_civilizations                   5个100。。。
# random_names                              要搞？
# scripted_effects                          首轮暂不处理
# scripted_loc                              首轮暂不处理
# scripted_triggers                         首轮暂不处理
# scripted_variables                        首轮暂不处理
# section_templates                         2.0.2
# sector_settings                           没东西
# sector_types                              首轮暂不处理
# ship_behaviors                            2.0.2
# ship_sizes                                2.0.2
# solar_system_initializers                 首轮暂不处理
# special_projects                          首轮暂不处理
# species_archetypes                        首轮暂不处理
# species_classes                           首轮暂不处理
# species_names                             首轮暂不处理
# species_rights                            首轮暂不处理
# starbase_buildings                        2.0.2
# starbase_levels                           2.0.2       未上传
# starbase_modules                          2.0.2
# starbase_types                            首轮暂不处理，舰船模拟器用来判断恒星基地类型的，整体可看作logic
# start_screen_messages                     首轮暂不处理
# star_classes                              2.0.2       已整合到planet_classes里
# static_modifiers                          2.0.2       未上传
# strategic_resources                       2.0.2
# subjects                                  2.0.2
# system_types                              首轮暂不处理
# technology                                2.0.2   需要科技图板，需要更恒星基地组件、武器组件、政策，智械和虫群科技名
# terraform                                 在搞
# tile_blockers                             2.0.2
# traditions                                2.0.2   需要传统树状图
# tradition_categories                      传统分类
# traits                                    2.0.2   需要特质分类模板
# war_goals                                 2.0.2
# achievements.txt                          首轮暂不处理，主要文字和图标怎么关联。。。
# alerts.txt                                要搞？
# message_types.txt                         要搞？
