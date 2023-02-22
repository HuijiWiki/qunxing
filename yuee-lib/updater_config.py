import configparser
import os


class UpdaterConfig(object):
    def __init__(self):
        self.__config = configparser.ConfigParser()

    def load_config(self, config_path, config_array):
        # 获取配置文件
        if not os.path.exists(config_path):
            print('未找到config.ini文件。已经自动生成，请进行填写。')
            for section_data in config_array:
                self.__config.add_section(section_data['key'])
                for key in section_data['list']:
                    self.__config.set(section_data['key'], key, "")
            self.__config.write(open(config_path, "w"))
            return False

        self.__config.read('config.ini')
        return True

    def get(self, section_key, key):
        try:
            return self.__config.get(section_key, key)
        except configparser.NoOptionError as e:
            raise Exception('该参数不存在，请检查程序或配置文件。\nError:' + str(e))
