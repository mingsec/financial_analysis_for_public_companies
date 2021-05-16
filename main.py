import os

# 从download_data文档中引入所有函数
from download_data import *
# 从download_data文档中引入所有函数
from save_data import *


if __name__ == '__main__':
    
    ''' 调用下载函数下载数据，每次下载完后询问是否继续下载 '''
    continue_or_not = True
    while continue_or_not:
        sava_data_to_database(download_public_companies_data())

        is_continue = input("是否继续下载数据（y/n)：")
        if is_continue == 'n' or is_continue == 'N':
            continue_or_not = False
        
        os.system('cls')