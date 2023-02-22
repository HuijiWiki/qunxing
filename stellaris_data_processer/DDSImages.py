import os
from PIL import Image
from danteng import Danteng


def get_dds_images(gfx_dir, should_process=True, up_dir=r'L:\python_working_dir\stellaris\gfx', un_process=None):
    if not should_process:
        return []
    if un_process is None:
        un_process = []
    if not os.path.exists(up_dir):
        os.mkdir(up_dir)
    for name in os.listdir(gfx_dir):
        file_path = os.path.join(gfx_dir, name)
        if os.path.isdir(file_path):
            un_process = un_process + get_dds_images(file_path, True, up_dir + '\\' + name)
        elif name[-4:] == '.dds':
            Danteng.log('处理' + file_path)
            try:
                im = Image.open(file_path, 'r')
                Image.Image.save(im, up_dir + '\\' + name[0:-4] + '.png')
            except:
                Danteng.log('处理' + file_path + '出错')
                un_process.append(file_path)
    return un_process
