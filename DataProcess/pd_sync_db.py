# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
# 将加工后的明细数据同步到mysql
import os
import sys
import argparse
import pandas as pd
from op_mysql import PdMysql, get_db_conf

# 项目人工投入统计表(按人员-项目)-201812.xlsx
def sync_table(engine, tablename='RY_YCOMS', xls_file='项目人工投入统计表.xlsx', xls_sheet=0, yyyymm='201812'):
    # mydb.execute_sql('delete from %s where 月份=\'%s\'' %(tablename, yyyymm))
    # mydb.commit()
    if (tablename.upper()=='PP'):
        sql_content='truncate table %s' %(tablename)
    else:
        sql_content='delete from %s where 月份=\'%s\'' %(tablename, yyyymm)
    cur=engine.execute(sql_content)
    print('[%s][rowcount=%d]' %(sql_content, cur.rowcount))
    df=pd.read_excel(xls_file, sheet_name=xls_sheet)
    # df=pd.DataFrame(data)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df.to_sql(name=tablename, con=engine, if_exists = 'append', index = False, index_label = False)
    # results = mydb.select_sql('SELECT count(*) FROM {} where 月份=\"{}\"'.format(tablename, yyyymm))
    if (tablename.upper()=='PP'):
        cur = engine.execute('SELECT count(*) FROM {}'.format(tablename))
    else:
        cur = engine.execute('SELECT count(*) FROM {} where 月份=\"{}\"'.format(tablename, yyyymm))
    results=cur.fetchall()
    if(df.iloc[:,0].size!=results[0][0]):
        raise("load data error, file[{}:{}], table[{}:{}]".format(xls_file, df.iloc[:,0].size, tablename, results[0][0]))  
    return results[0][0]

parser=argparse.ArgumentParser(description='同步数据到Database，并进行数据调整')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
parser.add_argument('--input', '-i', dest='inputfile', required=True, help='input excel file')
parser.add_argument('--table', '-t', dest='tablename', required=True, help='target table')
parser.add_argument('--yyyymm', '-d', dest='yyyymm', type=str, required=False, help='input yyyymm[201812]')

if __name__ == "__main__":
    # 测试用
    if(len(sys.argv) == 1):
        parser.print_help()
        args=parser.parse_args('--input F:/workspace/python/data/201812/pp-201812.xlsx --table PP'.split())
        # args=parser.parse_args('--input F:/workspace/python/data/201812/项目人工投入统计表(按人员-项目)-201812.xlsx --table RY_YCOMS -d 201812'.split())
    else:
        args=parser.parse_args()

    db_params=get_db_conf('database.ini')
    pdConn = PdMysql(**db_params)
    # mydb = Mysql(**db_params)
    func=globals().get('sync_table')
    if(func!=None):
        func(pdConn.engine, args.tablename, args.inputfile, yyyymm=args.yyyymm)
    else:
        raise("find function[{}] error".format('sync_table'))  

