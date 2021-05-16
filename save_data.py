""" 引入第三方模块 """
# 引入 pandas 模块
import pymysql



""" ===自定义函数集=== """
def sava_data_to_database(date_table):
    """ 保存数据至数据库

    创建数据库连接，打开数据库，并调用函数将数据存入 MySQL 数据库

    参数
    ----------
    date_table: list
        待存入数据库的数据
        
    返回值
    -------
    无
    """

    ''' 配置函数的参数 '''
    # 获取公司代码
    company_code = date_table[1][0][0]
     # 根据表格类型确定待写入数据的表名、字段名及字段值数量
    if date_table[0] == 'FD':
        table_name = 'financial_data'
        fileds = '公司代码, 报告日期, 项目编号, 值'
        field_values = r'%s, %s, %s, %s'
        data_type = "财务报表"
    elif date_table[0] == 'CI':
        table_name = 'corporation_information'
        fileds = '公司代码, 公司名称, 公司英文名称, 上市市场, 上市日期, 发行价格, 主承销商, 成立日期, 注册资本_万元,  机构类型, \
            组织形式, 董事会秘书, 公司电话, 董秘电话, 公司传真, 董秘传真, 公司电子邮箱, 董秘电子邮箱, 公司网址, 邮政编码, \
            信息披露网址, 证券简称更名历史, 注册地址, 办公地址, 公司简介, 经营范围'
        field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
        data_type = "公司信息"
    elif date_table[0] == 'II':
            table_name = 'issue_information'
            fileds = '公司代码, 上市地, 主承销商, 承销方式, 上市推荐人, 每股发行价_元, 发行方式, 发行市盈率_按发行后总股本, 首发前总股本_万股, 首发后总股本_万股, \
                实际发行量_万股, 预计募集资金_万元, 实际募集资金合计_万元, 发行费用总额_万元, 募集资金净额_万元, 承销费用_万元, 招股公告日, 上市日期'
            field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
            data_type = "发行信息"


    ''' 创建数据库连接及游标 '''
    DB = pymysql.connect(
        host='127.0.0.1', 
        port=3306, 
        user='root', 
        passwd='330715', 
        db='financial_analysis_for_public_companies')
    cursor = DB.cursor()
    
    ''' 由于下载的数据通常为全局数据，在下载前先检查数据库中是否有该公司的数据，
        如果有，则提示是否删除重新下载；否则退出下载过程。'''
    # check_data_is_in_database()
    # delete_date_in_database(company_code, report_code)
    cursor.execute(f"SELECT * FROM { table_name } WHERE 公司代码 = { company_code }")
    result = cursor.fetchone()
    if result != None:
        yes_or_no = input('该公司的数据已在数据库中，如需删除并重新保存请输入"y"：\n ')
        if yes_or_no =="y" or yes_or_no =="Y":
            cursor.execute(f"DELETE FROM { table_name } WHERE 公司代码 = { company_code }")
        else:
            print("取消保存数据。")
            return

    ''' 将数据写入数据库 '''
    print("开始向数据库写入" + data_type + "数据")
    cursor.executemany(f"INSERT INTO { table_name }({ fileds }) VALUES ({ field_values })", date_table[1])
    print("数据写入完毕")

    ''' 向数据库提交操作并关闭数据库连接 '''
    DB.commit()
    DB.close()

    print("数据保存成功！")

    return
