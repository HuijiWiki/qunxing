from collections import OrderedDict

from huijiWiki import HuijiWiki
import json


WIKI_KEY = 'qunxing'


# 登录模块
def log_in():
    # 创建wiki对象
    wiki = HuijiWiki(WIKI_KEY)
    if not wiki.login('DesertEagleF_bot', '..........'):
        print('登录失败')
        return False

    # 获取token
    if not wiki.get_edit_token():
        print('获取token失败')
        return False
    wiki.set_thread_number(4)
    return wiki


def cat_upload(cat_name, all_data, wiki, filepath='', summary='', compare_flag=True, is_upload=True):
    if not is_upload:
        return False
    for name in all_data:
        data = all_data[name]
        up_data = json.dumps(data)
        if filepath == '':
            filepath = 'J:\\wikitext\\' + WIKI_KEY + '\\data\\'
        itempath = 'J:\\wikitext\\' + WIKI_KEY + '\\item\\'

        # print(data['key'])
        filename = data['main_category'] + '\\' + data['key'] + '.json'
        page_name = cat_name + name
        # print(page_name)
        # F:\PycharmProjects\stellaris_data_processer\local_data
        # edit(self, title, text, filepath='', summary='', compare_flag=False):
        # 编辑
        # edit参数：
        # title：页面标题
        # text：页面编辑内容
        # 以上两个必填
        # summary：编辑摘要
        # filepath：一个本地文件路径，如果填写的话，页面成功编辑的情况下，会保存编辑内容为一个文本到这个文件
        # compare_flag：布尔值，默认False，如果为True的话，编辑内容会和filepath指定的文本文件进行内容对比，如果一样则跳过上传
        wiki.edit('Data:' + page_name + '.json', up_data, filepath + filename, summary, compare_flag)
        # 等待编辑进程完成
        # wiki.wait_threads()
        # print('Json编辑完成')

        # 单项页面
        #     upload_dict('Data:Technology/'+ item + '.json', technology[item])
        if data['main_category'] == 'deposits':
            text = '{{Item|' + data['key'] + '|title = ' + data['key'] + '}}[[Category:数据资料]]'
        else:
            text = '{{Item|' + data['key'] + '|title = ' + data['zhcn_name'] + '}}[[Category:数据资料]]'
        if data['main_category'] == 'technology':
            text = '{{Tech_card|' + data['key'] + '}}<br /><br />' + text
        elif data['main_category'] == 'buildings':
            text = '{{Building_icon|' + data['key'] + '}}<br /><br />' + text
        wiki.edit('Item:' + page_name, text, itempath + filename, summary, compare_flag)
        # 等待编辑进程完成
        # wiki.wait_threads()
        # print('Item编辑完成')
    return True


# data : OrderedDict格式的数据
# page_name : 页面名称，类似于'Data:Test/ethics.json'
def upload_dict(page_name, data, wiki, filepath='', summary='', compare_flag=True, is_upload=True):
    if not is_upload:
        return False
    up_data = json.dumps(data)

    if filepath == '':
        filepath = 'J:\\wikitext\\' + WIKI_KEY + '\\data\\'
    itempath = 'J:\\wikitext\\' + WIKI_KEY + '\\item\\'

    try:
        print(data['key'])
    except:
        z = 1

    filename = data['main_category'] + '\\' + data['key'] + '.json'
    wiki.edit('Data:' + page_name + '.json', up_data, filepath + filename, summary, compare_flag)

    # print('Json编辑完成')
    # 单项页面
    #     upload_dict('Data:Technology/'+ item + '.json', technology[item])
    text = '{{Item|' + data['key'] + '|title = ' + data['zhcn_name'] + '}}[[Category:数据资料]]'
    if data['main_category'] == 'technology':
        text = '{{Tech_card|' + data['key'] + '}}<br /><br />' + text
    elif data['main_category'] == 'buildings':
        text = '{{Building_icon|' + data['key'] + '}}<br /><br />' + text
    wiki.edit('Item:' + page_name, text, itempath + filename, summary, compare_flag)
    # 等待编辑进程完成
    # wiki.wait_threads()

    # print('Item编辑完成')
    return True
#
#
# if __name__ == '__main__':
#     a_data_page_name = 'Data:Unit_aaa.json'
#     a_data = OrderedDict([
#         ('name', 'aaa'),
#         ('type', 'attacker'),
#         ('datatype', 'Unit'),
#     ])
#     upload_dict(a_data_page_name, a_data)
