import os
from collections import OrderedDict

from DDSImages import get_dds_images
from StellarisFile import StellarisFile
from StellarisProcessor import processor
from danteng import Danteng
from localization import replace

game_path = r'I:\Games\SteamLibrary\steamApps\common\Stellaris'
beta_path = r'I:\Games\steam\steamapps\common\Stellaris Beta'
gfx_path = game_path + r'\gfx'
useful_paths = {
    'common': game_path + r'\common',
    'events': game_path + r'\events',
    'gfx': game_path + r'\Interface',
    'loc_en': game_path + r'\localisation\english',
    'loc_cn': game_path + r'\localisation\simp_chinese',
    'loc_re': beta_path + r'\localisation\simp_chinese'
}

TREE_DATA = r'tree_data.obj'
ALL_LOC = r'all_loc.obj'
RAW_DATA = r'raw_data.obj'
ALL_DATA = r'all_data.obj'


def get_data(purge=False):
    if not purge and os.path.exists(TREE_DATA):
        raw_tree = Danteng.load_obj(TREE_DATA)
        raw_data = Danteng.load_obj(RAW_DATA)
        raw_loc = Danteng.load_obj(ALL_LOC)
    else:
        raw_tree = OrderedDict()
        raw_data = OrderedDict()
        raw_loc = OrderedDict()
        for dir_name in os.listdir(useful_paths['common']):
            if os.path.isdir(os.path.join(useful_paths['common'], dir_name)):
                if dir_name == r'name_lists' or dir_name == r'random_names':
                    continue
                raw_tree[dir_name] = StellarisFile(dir_name, useful_paths)
            Danteng.log(dir_name + ' Done')
        raw_tree['events'] = StellarisFile(useful_paths['events'], useful_paths, other=True)
        raw_tree['gfx'] = StellarisFile(useful_paths['gfx'], useful_paths, other=True)
        Danteng.save_obj(raw_tree, TREE_DATA)
        for name in raw_tree:
            raw_data[name] = raw_tree[name].get_data()
            if len(raw_loc) == 0:
                raw_loc = raw_tree[name].get_loc()
        raw_loc['cn'] = replace(raw_loc['cn'])
        raw_loc['en'] = replace(raw_loc['en'])
        Danteng.save_obj(raw_data, RAW_DATA)
        Danteng.save_obj(raw_loc, ALL_LOC)
    return raw_tree, raw_data, raw_loc


def begin(settings):
    Danteng.log('————————————————处理图片————————————————')
    un_process_image = get_dds_images(gfx_path, settings['process_image'])
    Danteng.log('————————————————读取数据————————————————')
    tree_data, raw, all_loc = get_data(settings['get_new_data'])
    Danteng.log('————————————————处理数据————————————————')
    processed_data = processor(raw, all_loc, settings['version'])

    return un_process_image, processed_data


if __name__ == '__main__':
    # all settings are here
    un_processed_image, all_data = begin({
        'process_image': False,     # Do I need new image?
        'get_new_data': True,      # Do I need new data?
        'version': '2.8.1',         # Is it the newest version?
    })
    z = 1
