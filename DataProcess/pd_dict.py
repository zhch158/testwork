# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import argparse
import pandas as pd
from op_mysql import PdMysql, get_db_conf

def pd_branch_fromfile(xls_file, xls_sheet=0, o_file="branch.xlsx"):
    lev=lev1=lev2=lev3=lev4=lev5=''
    lev1_name=lev2_name=lev3_name=lev4_name=lev5_name=''
    data=pd.read_excel(xls_file, sheet_name=xls_sheet)
    df=pd.DataFrame(data)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))

    out_columns=list(df.columns) + ['lev1', 'lev1_name', 'lev2', 'lev2_name', 'lev3', 'lev3_name', 'lev4', 'lev4_name', 'lev5', 'lev5_name', 'lev']
    out_df=pd.DataFrame(columns=out_columns)

    i=0
    branch_row=df.loc[df['部门编号'].astype('str')=='1']
    lev1=str(branch_row['部门编号'].values[0])
    lev1_name=branch_row['部门名称'].values[0]
    for index,row in df.iterrows():
        # print(index)
        # print(row)
        if(len(str(row['部门编号']))==1):
            lev='1'
            lev2=lev3=lev4=lev5=''
            lev2_name=lev3_name=lev4_name=lev5_name=''
        elif(len(str(row['部门编号']))==3 or len(str(row['部门编号']))==4):
            lev='2'
            lev2=str(row['部门编号'])
            lev2_name=row['部门名称']
            lev3=lev4=lev5=''
            lev3_name=lev4_name=lev5_name=''
        elif(len(str(row['部门编号']))==5):
            lev='3'
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:3]]
            lev2=str(branch_row['部门编号'].values[0])
            lev2_name=branch_row['部门名称'].values[0]
            lev3=str(row['部门编号'])
            lev3_name=row['部门名称']
            lev4=lev5=''
            lev4_name=lev5_name=''
        elif(len(str(row['部门编号']))==7):
            lev='4'
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:3]]
            lev2=str(branch_row['部门编号'].values[0])
            lev2_name=branch_row['部门名称'].values[0]
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:5]]
            lev3=str(branch_row['部门编号'].values[0])
            lev3_name=branch_row['部门名称'].values[0]
            lev4=str(row['部门编号'])
            lev4_name=row['部门名称']
            lev5=''
            lev5_name=''
        elif(len(str(row['部门编号']))==9):
            lev='5'
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:3]]
            lev2=str(branch_row['部门编号'].values[0])
            lev2_name=branch_row['部门名称'].values[0]
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:5]]
            lev3=str(branch_row['部门编号'].values[0])
            lev3_name=branch_row['部门名称'].values[0]
            branch_row=df.loc[df['部门编号'].astype('str')==str(row['部门编号'])[:7]]
            lev4=str(branch_row['部门编号'].values[0])
            lev4_name=branch_row['部门名称'].values[0]
            lev5=str(row['部门编号'])
            lev5_name=row['部门名称']

        out_df.loc[i]=list(row) + [lev1, lev1_name, lev2, lev2_name, lev3, lev3_name, lev4, lev4_name, lev5, lev5_name, lev]
        i+=1
    
    out_df.to_excel(o_file, encoding='utf-8', sheet_name='部门列表', index=False, header=True)

def pd_branch(engine, o_file="branch.xlsx"):
    sql_content="SELECT distinct IFNULL(t.项目所属部门级四, ifnull(t.项目所属部门级三, ifnull(t.项目所属部门级二, t.项目所属部门级一))) as '部门名称',	'北京宇信科技集团股份有限公司' as lev1_name, t.项目所属部门级一 as lev2_name, t.项目所属部门级二 as lev3_name, t.项目所属部门级三 as lev4_name, t.项目所属部门级四 as lev5_name FROM RY_YCOMS t order by 2,3,4,5"
    df=pd.read_sql(sql_content, engine)
    print("table[%s], rows[%d], cols[%d]" %('RY_YCOMS', df.iloc[:,0].size, df.columns.size))
    df.to_excel(o_file, encoding='utf-8', sheet_name='部门列表', index=False, header=True)

def pd_project(engine, o_file="project.xlsx"):
    sql_content="SELECT distinct t.项目编号, t.项目名称, t.项目类型, t.项目所属部门级一, t.项目所属部门级二, t.项目所属部门级三, t.项目所属部门级四 FROM RY_YCOMS t WHERE t.项目名称 LIKE '%%部门管理' OR t.项目名称 LIKE '%%部门闲置' OR t.项目名称 LIKE '%%部门休假' order by 1"
    df=pd.read_sql(sql_content, engine)
    print("table[%s], rows[%d], cols[%d]" %('RY_YCOMS', df.iloc[:,0].size, df.columns.size))
    df.loc[df['项目名称'].str.contains('.*部门管理'), '项目类型']= '部门管理'
    df.loc[df['项目名称'].str.contains('.*部门闲置'), '项目类型']= '部门闲置'
    df.loc[df['项目名称'].str.contains('.*部门休假'), '项目类型']= '部门休假'
    df.to_excel(o_file, encoding='utf-8', sheet_name='管理、闲置、休假', index=False, header=True)

parser=argparse.ArgumentParser(description='生成部门列表，日常管理、闲置项目清单')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
# parser.add_argument('--input', '-i', dest='inputfile', required=True, help='input excel file')
parser.add_argument('--method', '-m', dest='method', required=True, help='选择调用方法', choices=['pd_branch', 'pd_project'])
parser.add_argument('--output', '-o', dest='outputfile', required=True, help='output excel file')

if __name__ == "__main__":
    # 测试用
    if(len(sys.argv) == 1):
        parser.print_help()
        # args=parser.parse_args('--input F:/workspace/python/data/201811/执行中组织结构基本信息表-20181225130600.xlsx --output F:/workspace/python/data/201811/部门列表-201812.xlsx -m pd_branch'.split())
        # args=parser.parse_args('--output F:/workspace/python/data/201812/BRANCH-RY-201812.xlsx -m pd_branch'.split())
        args=parser.parse_args('--output F:/workspace/python/data/201812/PROJECT-RY-201812.xlsx -m pd_project'.split())
    else:
        args=parser.parse_args()

    db_params=get_db_conf('database.ini')
    pdConn = PdMysql(**db_params)
    func=globals().get(args.method)
    if(func!=None):
        func(pdConn.engine, args.outputfile)
    else:
        raise("find function[{}] error".format(args.method))  

