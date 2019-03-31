# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import argparse
import pandas as pd
from op_mysql import Mysql, PdMysql, get_db_conf

def sync_pp(engine, tablename='PP', xls_file='pp.xlsx', xls_sheet=0, yyyymm=None):
    sql_content='truncate table %s' %(tablename)
    cur=engine.execute(sql_content)
    print('[%s][rowcount=%d]' %(sql_content, cur.rowcount))
    df=pd.read_excel(xls_file, sheet_name=xls_sheet)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False)
    cur = engine.execute("SELECT count(*) FROM {}".format(tablename))
    results=cur.fetchall()
    if(df.iloc[:,0].size!=results[0][0]):
        raise("load data error, file[{}:{}], table[{}:{}]".format(xls_file, df.iloc[:,0].size, tablename, results[0][0]))  
    return results[0][0]

# 项目人工投入统计表(按人员-项目)-201812.xlsx
def sync_workload(engine, tablename='RY_YCOMS', xls_file='项目人工投入统计表.xlsx', xls_sheet=0, yyyymm='201812'):
    # mydb.execute_sql('delete from %s where 月份=\'%s\'' %(tablename, yyyymm))
    # mydb.commit()
    sql_content='delete from %s where 月份=\'%s\'' %(tablename, yyyymm)
    cur=engine.execute(sql_content)
    print('[%s][rowcount=%d]' %(sql_content, cur.rowcount))
    df=pd.read_excel(xls_file, sheet_name=xls_sheet)
    # df=pd.DataFrame(data)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False)
    # results = mydb.select_sql('SELECT count(*) FROM {} where 月份=\"{}\"'.format(tablename, yyyymm))
    cur = engine.execute('SELECT count(*) FROM {} where 月份=\"{}\"'.format(tablename, yyyymm))
    results=cur.fetchall()
    if(df.iloc[:,0].size!=results[0][0]):
        raise("load data error, file[{}:{}], table[{}:{}]".format(xls_file, df.iloc[:,0].size, tablename, results[0][0]))  
    return results[0][0]

parser=argparse.ArgumentParser(description='同步数据到Database，并进行数据调整')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
parser.add_argument('--input', '-i', dest='inputfile', nargs=1, required=True, help='input excel file')
parser.add_argument('--table', '-t', dest='tablename', nargs=1, required=True, help='target table')
parser.add_argument('--method', '-m', dest='method', nargs=1, required=True, help='load data method', choices=['sync_pp', 'sync_workload'])
parser.add_argument('--yyyymm', '-d', dest='yyyymm', type=str, nargs=1, required=False, help='input yyyymm[201812]')

if __name__ == "__main__":
    # 测试用
    if(len(sys.argv) == 1):
        parser.print_help()
        args=parser.parse_args('--method sync_pp --input F:/workspace/python/data/201812/pp-201812.xlsx --table PP'.split())
        # args=parser.parse_args('--method sync_workload --input F:/workspace/python/data/201812/项目人工投入统计表(按人员-项目)-201812.xlsx --table RY_YCOMS -d 201812'.split())
    else:
        args=parser.parse_args()

    db_params=get_db_conf('database.ini')
    pdConn = PdMysql(**db_params)
    # mydb = Mysql(**db_params)
    if(args.method[0]=='sync_pp'):
        sync_pp(pdConn.engine, args.tablename[0], args.inputfile[0])
    elif(args.method[0]=='sync_workload'):
        sync_workload(pdConn.engine, args.tablename[0], args.inputfile[0], yyyymm=args.yyyymm[0])
