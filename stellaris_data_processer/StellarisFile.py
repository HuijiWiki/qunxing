
# statics
import os
from collections import OrderedDict

from ParadoxFile import ParadoxFile

unprocessed = []


class StellarisFile:
    all_loc = OrderedDict()
    all_data = OrderedDict()
    has_loc = False

    def __init__(self, path, useful_paths, base_path='common', other=False):
        self.cat = path
        self.useful_paths = useful_paths
        if not other:
            self.path = os.path.join(useful_paths[base_path], path)
        else:
            self.path = path
        self.data = OrderedDict()
        self.set_loc()
        self.get_cat_files()

    def set_loc(self):
        if not self.has_loc:
            temp_all_loc = OrderedDict()
            temp_all_loc['en'] = self.get_files(self.useful_paths['loc_en'])
            temp_all_loc['cn'] = self.get_files(self.useful_paths['loc_cn'])
            temp_all_loc['cn'].update(self.get_files(self.useful_paths['loc_re']))
            self.all_loc['en'] = OrderedDict()
            self.all_loc['cn'] = OrderedDict()
            for file_name in temp_all_loc['en']:
                for name in temp_all_loc['en'][file_name]:
                    self.all_loc['en'][name] = temp_all_loc['en'][file_name][name]
            for file_name in temp_all_loc['cn']:
                for name in temp_all_loc['cn'][file_name]:
                    self.all_loc['cn'][name] = temp_all_loc['cn'][file_name][name]
            self.has_loc = True

    def get_cat_files(self):
        if 'Interface' in self.path:
            self.data['icons.gfx'] = self.one_file(self.path, 'icons.gfx', unprocessed)
            self.data['eventpictures.gfx'] = self.one_file(self.path, 'eventpictures.gfx', unprocessed)
            z = 5
        else:
            self.data = self.get_files(self.path)
        self.all_data[self.cat] = self.data

    def get_files(self, path):
        data = OrderedDict()
        for name in os.listdir(path):
            sub = os.path.join(path, name)
            if os.path.isdir(sub):
                data[name] = OrderedDict()
                for sub_name in os.listdir(sub):
                    data[name][sub_name] = self.one_file(sub, sub_name, unprocessed)
            else:
                data[name] = self.one_file(path, name, unprocessed)
        return data

    @staticmethod
    def one_file(path, name, unprocessed):
        file_object = ParadoxFile(path, name, unprocessed)
        return file_object.get_data()

    def get_data(self):
        return self.data

    def get_loc(self):
        return self.all_loc
