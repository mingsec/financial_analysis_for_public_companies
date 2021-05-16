""" 引入系统模块 """
import datetime
import re
# 从 decimal 模块中的 Decimal、getcontext 函数，以设置货币类型
from decimal import Decimal, getcontext

""" 引入第三方模块 """
# 引入 pandas 模块
import pandas



""" 设置全局变量参数 """
# 设置货币的有效数字
getcontext().prec = 22


""" ===自定义函数集=== """
def download_public_companies_data():
    """ 调用函数从互联网下载上市公司数据。

    参数
    -------
    无

    返回值
    -------
    origin_data：list，待写入数据库表的数据

    """

    ''' 配置函数的参数 '''
    origin_data= []


    ''' 手工输入需下载数据的上市公司的公司代码 '''
    company_code = input("请输入上市公司的公司代码：")

    ''' 手工输入需下载数据的上市公司的数据类型'''
    report_code = input("请输入需下载的上市公司数据类型：\n 1 - 财务数据\n 2 - 公司信息\n 3 - 发信信息\n 请输入需下载的数据类型：")

    ''' 根据待下载的数据类型调用函数 '''
    if report_code == '1':
        origin_data = get_financial_data_from_SINA(company_code)                      
    elif report_code == '2':
        origin_data = get_corporation_information_from_SINA(company_code)              
    elif report_code == '3':
        origin_data = get_issue_information_from_SINA(company_code)
    else:
        print("暂不支持下载的数据类型，请重输入。")
        return

    return origin_data


def get_financial_data_from_SINA(company_code):
    """ 从新浪财经网下载上市公司财务数据。
    
    参数
    -------
    company_code：str
        公司代码，6位数

    返回值
    -------
    origin_data：list
        待写入数据库表的数据

    """
    
    ''' 配置函数的参数 '''
    origin_data = []

    ''' 下载数据，并将数据由二维表转为一维表 '''
    # 可供下载的财务报备类型：1--资产负债表，2--利润表，3--现金流量表。
    for statement_type_code in range(1, 4):
        # 根据报表编号确定报表类型、名称以及科目前缀 
        if statement_type_code == 1:
            statement_type = 'BalanceSheet'
            statement_name = '资产负债表'
            front_name = 'BS-'
        elif statement_type_code == 2:
            statement_type = 'ProfitStatement'
            statement_name = '利润表'
            front_name = 'PS-'
        elif statement_type_code == 3:
            statement_type = 'CashFlow'
            statement_name = '现金流量表'
            front_name = 'CF-'
        else:
            print("报表类型选择错误，请重新选择！")
            return

        print("开始下载" + company_code + "的" + statement_name + "...")
        # 配置下载数据的URL
        url = 'http://money.finance.sina.com.cn/corp/go.php/vDOWN_' + statement_type + '/displaytype/4/stockid/' + company_code + '/ctrl/all.phtml'
        # 下载数据，并保存为 pandas 的数据框架
        # 尽管下载的过来的数据为 .xls 格式的文档，但实际为 csv 格式的文档，所以用 read_csv() 函数，同时按 ‘\t’ 进行数据切分
        page_data = pandas.read_csv(url, encoding='gbk', header=None, sep='\t')
        print("数据下载完毕")
    
        print("开始处理数据...")
        # 将二维数据表转为一维数据表，并转换数据类型
        # --.shape[0] 返回 dataframe 的行数
        # --.shape[1] 返回 dataframe 的列数
        for column in range(1, page_data.shape[1]-2):
            for row in range(2, page_data.shape[0]):
                # 去除值为 ’0‘ 或 nan 的行 
                if pandas.isnull(page_data.iloc[row, column]) or page_data.iloc[row, column] == '0':
                    continue
                # 转换获取的数据的数据格式
                subject_number = front_name + str(row)
                report_date = datetime.datetime.strptime(str(page_data.iloc[0, column]), r'%Y%m%d').date()
                value = Decimal(page_data.iloc[row, column]).quantize(Decimal('0.00'))
                # 向一维数据表（list）添加数据
                origin_data.append([company_code, report_date, subject_number, value]) 
        print("数据处理完毕！")
    
    return ['FD', origin_data]


def get_corporation_information_from_SINA(company_code):
    """ 从新浪财经网下载上市公司财务数据。
    
    参数
    -------
    company_code：str
        公司代码，6位数

    返回值
    -------
    origin_data：list
        待写入数据库表的数据

    """
    
    ''' 配置函数的参数 '''
    origin_data = {}
    
    ''' 获取包含公司资料的网页，并下载数据 '''
    print("开始下载" + company_code + "的公司资料数据...")
    # 配置下载数据的 URL 
    url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/' + company_code + '.phtml'
    # 下载数据，所需的数据在 pandas 读取的页面的表格中的第 4 个中
    page_data = pandas.read_html(url)[3]
    print("数据下载完毕")
    
    ''' 将 dataframe 中的数据整理成字典，并转换数据类型 '''
    print("开始处理数据...") 
    origin_data['公司代码'] = company_code
    origin_data['公司名称'] = page_data.iloc[0, 1]
    origin_data['公司英文名称'] = page_data.iloc[1, 1]
    origin_data['上市市场'] = page_data.iloc[2, 1]
    origin_data['上市日期'] = datetime.datetime.strptime(str(page_data.iloc[2, 3]), r'%Y-%m-%d').date()
    origin_data['发行价格'] = Decimal(page_data.iloc[3, 1]).quantize(Decimal('0.00'))
    origin_data['主承销商'] = page_data.iloc[3, 3]
    origin_data['成立日期'] = datetime.datetime.strptime(str(page_data.iloc[4, 1]), r'%Y-%m-%d').date()
    origin_data['注册资本(万元)'] = Decimal(re.findall('\d+',page_data.iloc[4, 3])[0]).quantize(Decimal('0.00'))
    origin_data['机构类型'] = page_data.iloc[5, 1]
    origin_data['组织形式'] = page_data.iloc[5, 3]
    origin_data['董事会秘书'] = page_data.iloc[6, 1]
    origin_data['公司电话'] = page_data.iloc[6, 3]
    origin_data['董秘电话'] = page_data.iloc[8, 1]
    origin_data['公司传真'] = page_data.iloc[8, 3]
    origin_data['董秘传真'] = page_data.iloc[10, 1]
    origin_data['公司电子邮箱'] = page_data.iloc[10, 3]
    origin_data['董秘电子邮箱'] = page_data.iloc[12, 1]
    origin_data['公司网址'] = page_data.iloc[12, 3]
    origin_data['邮政编码'] = page_data.iloc[14, 1]
    origin_data['信息披露网址'] = page_data.iloc[14, 3]
    origin_data['证券简称更名历史'] = page_data.iloc[16, 1]
    origin_data['注册地址'] = page_data.iloc[17, 1]
    origin_data['办公地址'] = page_data.iloc[18, 1]
    origin_data['公司简介'] = page_data.iloc[19, 1]
    origin_data['经营范围'] = page_data.iloc[20, 1]

    ''' 清洗字典中的异常值 '''
    for key in origin_data:
        # 将空值替换为 ‘--’
        if pandas.isna(origin_data[key]):
            origin_data[key] = '--'
        # 将 '\r\n'、' '、'"'、"'"去除
        if isinstance(origin_data[key], str):
            origin_data[key] = origin_data[key].replace('\r\n', '')
            origin_data[key] = origin_data[key].replace(' ', '')
            origin_data[key] = origin_data[key].replace('"', '')
            origin_data[key] = origin_data[key].replace("'", '')

    print("数据处理完毕")

    return ['CI', [list(origin_data.values())]]


def get_issue_information_from_SINA(company_code):
    """ 从新浪财经网下载上市公司财务数据。
    
    参数
    -------
    company_code：str
        公司代码，6位数

    返回值
    -------
    origin_data：list
        待写入数据库表的数据

    """
    
    ''' 配置函数的参数 '''
    origin_data = {}

    ''' 获取包含发行情况的网页，并下载数据 '''
    print("开始下载" + company_code + "的发行情况数据...")
    # 配置下载数据的 URL 
    url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_NewStock/stockid/' + company_code + '.phtml'
    # 下载数据，所需的数据在 pandas 读取的页面的表格中的第 13 个中
    page_data = pandas.read_html(url)[12]
    print("数据下载完毕")

    ''' 将 dataframe 中的数据整理成字典，并转换数据类型 '''
    print("开始处理数据...")
    origin_data['公司代码'] = company_code
    origin_data['上市地'] = page_data.iloc[0, 1]
    origin_data['主承销商'] = page_data.iloc[1, 1]
    origin_data['承销方式'] = page_data.iloc[2, 1]
    origin_data['上市推荐人'] = page_data.iloc[3, 1]
    origin_data['每股发行价(元)'] = Decimal(page_data.iloc[4, 1]).quantize(Decimal('0.00'))
    origin_data['发行方式'] = page_data.iloc[5, 1]
    origin_data['发行市盈率(按发行后总股本)'] = Decimal(page_data.iloc[6, 1]).quantize(Decimal('0.00'))
    origin_data['首发前总股本(万股)'] = Decimal(page_data.iloc[7, 1]).quantize(Decimal('0.00')) 
    origin_data['首发后总股本(万股)'] = Decimal(page_data.iloc[8, 1]).quantize(Decimal('0.00')) 
    origin_data['实际发行量(万股)'] = Decimal(page_data.iloc[9, 1]).quantize(Decimal('0.00'))
    origin_data['预计募集资金(万元)'] = Decimal(page_data.iloc[10, 1]).quantize(Decimal('0.00'))
    origin_data['实际募集资金合计(万元)'] = Decimal(page_data.iloc[11, 1]).quantize(Decimal('0.00'))
    origin_data['发行费用总额(万元)'] = Decimal(page_data.iloc[12, 1]).quantize(Decimal('0.00'))
    origin_data['募集资金净额(万元)'] = Decimal(page_data.iloc[13, 1]).quantize(Decimal('0.00'))
    origin_data['承销费用(万元)'] = Decimal(page_data.iloc[14, 1]).quantize(Decimal('0.00'))
    origin_data['招股公告日'] = datetime.datetime.strptime(str(page_data.iloc[15, 1]), r'%Y-%m-%d').date()
    origin_data['上市日期'] = datetime.datetime.strptime(str(page_data.iloc[16, 1]), r'%Y-%m-%d').date()
    
    ''' 清理字典中的异常值 (nan) '''
    for key in origin_data:  
        # 将空值替换为 ‘--’
        if pandas.isna(origin_data[key]):
            origin_data[key] = '--'
        # 将 '\r\n'、' '、'"'、"'"去除
        if isinstance(origin_data[key], str):
            origin_data[key] = origin_data[key].replace('\r\n', '')
            origin_data[key] = origin_data[key].replace(' ', '')
            origin_data[key] = origin_data[key].replace('"', '')
            origin_data[key] = origin_data[key].replace("'", '')

    print("数据处理完毕")

    return ['II', [list(origin_data.values())]]