# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
# 将加工后的明细数据同步到mysql
import os
import sys
import argparse
import pandas as pd
from op_mysql import PdMysql, get_db_conf

def pre_action (engine, tablename=None, sql_content=None, yyyymm='201901'):
    if(sql_content==None):
        if (tablename!=None and tablename.upper() in ['PP', '归属条线', '外包项目', '部门列表', '考核单元', '国有大行客户名称']):
            sql_content='truncate table %s' %(tablename)
        else:
            sql_content='delete from %s where 月份=\'%s\'' %(tablename, yyyymm)
    if(sql_content):
        cur=engine.execute(sql_content)
        print('[%s][rowcount=%d]' %(sql_content, cur.rowcount))
    return cur.rowcount

def after_action(engine, insert_rows, tablename=None, sql_content=None, yyyymm='201901'):
    if(sql_content==None):
        if (tablename!=None and tablename.upper() in ['PP', '归属条线', '外包项目', '部门列表', '考核单元', '国有大行客户名称']):
            sql_content='SELECT count(*) FROM {}'.format(tablename)
        else:
            sql_content = 'SELECT count(*) FROM {} where 月份=\"{}\"'.format(tablename, yyyymm)

    if(sql_content):
        cur = engine.execute(sql_content)
        results=cur.fetchall()
    if(insert_rows!=results[0][0]):
        raise Exception("load data error, file[%d], table[%s, %d]" %(insert_rows, sql_content, results[0][0]))  
    return results[0][0]

def sync_action(engine, tablename='RY_YCOMS', xls_file='项目人工投入统计表.xlsx', xls_sheet_list=[0], yyyymm='201812'):
    rows=0
    for sheet_inx in xls_sheet_list:
        df=pd.read_excel(xls_file, sheet_name=sheet_inx)
        # df=pd.DataFrame(data)
        print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
        df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False, chunksize=10000)
        rows+=df.iloc[:,0].size
    return rows

# PP, RY_YCOMS, 外包项目, 考核单元, 归属条线
def sync_table(engine, tablename='RY_YCOMS', xls_file='项目人工投入统计表.xlsx', yyyymm='201812'):
    del_rows=pre_action (engine, tablename, yyyymm=yyyymm)
    insert_rows=sync_action(engine, tablename, xls_file, [0], yyyymm)
    after_action(engine, insert_rows, tablename, yyyymm=yyyymm)

def sync_xmmx(engine, tablename='项目损益明细', xls_file='项目损益明细.xlsx', yyyymm='201812'):
    rows=0
    del_rows=pre_action (engine, tablename, yyyymm=yyyymm)
    df_dict=pd.read_excel(xls_file, sheet_name=None)
    for sheet_name, df in df_dict.items():
        print("sheet[%s], rows[%d], cols[%d]" %(sheet_name, df.iloc[:,0].size, df.columns.size))
        df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False, chunksize=10000)
        rows+=df.iloc[:,0].size
    after_action(engine, rows, tablename, yyyymm=yyyymm)

def sync_fxmmx(engine, tablename='非项目损益明细', xls_file='非项目损益明细.xlsx', yyyymm='201812'):
    rows=0
    del_rows=pre_action (engine, tablename, yyyymm=yyyymm)
    df_dict=pd.read_excel(xls_file, sheet_name=None)
    for sheet_name, df in df_dict.items():
        print("sheet[%s], rows[%d], cols[%d]" %(sheet_name, df.iloc[:,0].size, df.columns.size))
        for spec in ['考核口径', '管理口径', '验收口径']:
            df['口径']=spec
            df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False, chunksize=10000)
            rows+=df.iloc[:,0].size
    after_action(engine, rows, tablename, yyyymm=yyyymm)

parser=argparse.ArgumentParser(description='同步数据到Database，并进行数据调整')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
parser.add_argument('--input', '-i', dest='inputfile', required=True, help='input excel file')
parser.add_argument('--table', '-t', dest='tablename', required=True, help='target table')
parser.add_argument('--yyyymm', '-d', dest='yyyymm', type=str, required=False, help='input yyyymm[201812]')
parser.add_argument('--method', '-m', dest='method', required=True, help='选择调用方法', choices=['sync_table', 'sync_xmmx', 'sync_fxmmx'])

if __name__ == "__main__":
    # 测试用
    args=list()
    if(len(sys.argv) == 1):
        parser.print_help()
        # args.append(parser.parse_args('--input F:/workspace/python/data/201812/pp-201812.xlsx --table PP -m sync_table'.split()))
        # args.append(parser.parse_args('--input F:/workspace/python/data/201812/项目人工投入统计表(按人员-项目)-201812.xlsx --table RY_YCOMS -d 201812 -m sync_table'.split()))
        # args.append(parser.parse_args('--input F:/workspace/python/data/201812/项目损益明细表-201812.xlsx --table 项目损益明细 -d 201812 -m sync_xmmx'.split()))
        args.append(parser.parse_args('--input F:/workspace/python/data/201812/非项目损益明细表-201812.xlsx --table 非项目损益明细 -d 201812 -m sync_fxmmx'.split()))
    else:
        args.append(parser.parse_args())

    db_params=get_db_conf('database.ini')
    pdConn = PdMysql(**db_params)
    # mydb = Mysql(**db_params)
    for arg in args:
        func=globals().get(arg.method)
        if(func!=None):
            func(pdConn.engine, arg.tablename, arg.inputfile, yyyymm=arg.yyyymm)
        else:
            raise Exception("find function[{}] error".format('sync_table'))  
