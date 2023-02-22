from collections import OrderedDict

from StellarisNew import Ethics, Agendas, Traits, ScriptedTriggers, Interface, GovSeries, StrategicResources, \
    DepositCategories, Deposits, Subjects, PopFactionTypes


def processor(raw, all_loc, version):
    all_data = OrderedDict()

    reflex_dict = {
        'gfx': Interface,
        # 'scripted variables': ScriptedVariables,
        'scripted_triggers': ScriptedTriggers,
        'strategic_resources': StrategicResources,
        'ethics': Ethics,
        'agendas': Agendas,
        'traits': Traits,
        'governments': GovSeries,   # authorities, governments, civics & origins
        'deposit_categories': DepositCategories,
        'deposits': Deposits,
        'subjects': Subjects,
        'pop_faction_types': PopFactionTypes,
        # 'war_goals': WarGoals,
        # 'casus_belli': CasusBelli,
        # 'planet_classes': PlanetClasses,
        # 'star_classes': StarClasses,
        # 'terraform': Terraform,
        # 'static_modifiers': StaticModifiers,
        # 'planet_modifiers': PlanetModifiers,
        # 'districts': Districts,
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
        # 'tradition_categories': TraditionCategory,
        # 'traditions': Traditions,
        # 'ascension_perks': AscensionPerks,
        # 'edicts': Edicts,
        # 'decisions': Decisions,
        # 'armies': Armies,
        # 'pop_categories': PopCategories,
        # 'pop_jobs': PopJobs,
        # 'relics': Relics,
        # 'megastructures': Megastructures,
        # 'buildings': Buildings,
        # 'technology': Technology,
        # 'achievements': Achievements,
        # 'events': Events,
    }
    for category in reflex_dict:
        if category in raw:
            all_data[category] = reflex_dict[category](raw[category], category, all_loc, version)
        else:
            z = 4
    z = 1
    return all_data

# achievements
# achievements.txt
# agendas                               done
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
# deposit_categories
# diplomacy_economy
# diplomatic_actions
# diplo_phrases
# districts
# economic_categories
# economic_plans
# edicts
# ethics                                done
# event_chains
# fallen_empires
# federation_laws
# federation_law_categories
# federation_perks
# federation_types
# galactic_focuses
# game_rules
# global_ship_designs
# governments                           done
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
# strategic_resources
# subjects
# system_types
# technology
# terraform
# trade_conversions
# traditions
# tradition_categories
# traits                                done
# war_goals

