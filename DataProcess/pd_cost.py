# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import argparse
import getopt
import pandas as pd

def set_value(project, lev3_name, col_name, prefix='', suffix=''):
    row=project.loc[project['项目所属部门级三']==lev3_name]
    if(row.size>0):
        return row[col_name].values[0]
    return prefix + lev3_name + suffix

def pd_direct_cost(xls_file, xls_sheet=0, xls_project=None, yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['所属一级部', '所属二级部', '项目编号', '项目名称', '项目状态', '项目预算数', '累计实际数', '当年实际数', '预算剩余', '全年预算执行比', '是否超预算']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df=df.fillna(method='ffill')
    df=df.loc[df['所属二级部'].str.contains('汇总', regex=True)==False]

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    res_df['项目编号']=df['项目编号']
    res_df['项目名称']=df['项目名称']
    res_df['项目状态']=df['项目状态']
    res_df['所属部门级一']=df['所属一级部']
    res_df['所属部门级二']=df['所属二级部']
    res_df['累计总成本']=df['累计实际数']
    res_df['当年累计成本']=df['当年实际数']
    res_df.loc[res_df['项目编号'].str.contains('.*-S'), '项目类型']= '售前项目'
    res_df.loc[res_df['项目编号'].str.contains('.*-E'), '项目类型']= '内部管理'
    res_df.loc[res_df['项目编号'].str.contains('.*-B'), '项目类型']= '产品研发'

    res_df['月份']=yyyymm
    # res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    # res_df['口径']='管理口径'
    # res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    # res_df['口径']='验收口径'
    # res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

def pd_manage_cost(xls_file, xls_sheet=0, xls_project='project.xlsx', yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['所属一级部', '所属二级部', '部门总累计实际数  ']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    #向下填充
    df=df.fillna(method='ffill')
    #过滤掉汇总行
    df=df.loc[df['所属二级部'].str.contains('汇总', regex=True)==False]

    project=pd.read_excel(xls_project, sheet_name=0)

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    res_df['所属部门级二']=df['所属一级部']
    res_df['所属部门级三']=df['所属二级部']
    # res_df['项目编号']=df['所属二级部'].apply(lambda x: set_value(x, 'YTEC-2019-', '-W'))
    # res_df['项目名称']=df['所属二级部'].apply(lambda x:set_value(x, suffix='-部门管理'))
    res_df['项目编号']=df.apply(lambda row: set_value(project, row['所属二级部'], '项目编号', 'YTEC-2019-', '-W'), axis=1)
    res_df['项目名称']=df.apply(lambda row: set_value(project, row['所属二级部'], '项目名称', suffix='-部门管理'), axis=1)
    res_df['所属部门级一']=df.apply(lambda row: set_value(project, row['所属二级部'], '项目所属部门级一'), axis=1)
    res_df['累计总成本']=df['部门总累计实际数  ']
    res_df['当年累计成本']=df['部门总累计实际数  ']

    res_df['月份']=yyyymm
    res_df['项目类型']='部门管理'
    res_df['项目状态']='考勤报工'
    # res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

def pd_idle_cost(xls_file, xls_sheet=0, xls_project='project.xlsx', yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['一级部名称', '二级部名称', '累计至今部门闲置实际支出']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df=df.fillna(method='ffill')
    df=df.loc[df['二级部名称'].str.contains('汇总', regex=True)==False]

    project=pd.read_excel(xls_project, sheet_name=0)

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    res_df['所属部门级二']=df['一级部名称']
    res_df['所属部门级三']=df['二级部名称']
    res_df['项目编号']=df.apply(lambda row: set_value(project, row['二级部名称'], '项目编号', 'YTEC-2019-', '-Y'), axis=1)
    res_df['项目名称']=df.apply(lambda row: set_value(project, row['二级部名称'], '项目名称', suffix='-部门闲置'), axis=1)
    res_df['所属部门级一']=df.apply(lambda row: set_value(project, row['二级部名称'], '项目所属部门级一'), axis=1)
    res_df['累计总成本']=df['累计至今部门闲置实际支出']
    res_df['当年累计成本']=df['累计至今部门闲置实际支出']

    res_df['月份']=yyyymm
    res_df['项目状态']='考勤报工'
    res_df['项目类型']='部门闲置'
    res_df.loc[res_df['项目编号'].str.contains('.*-Y'), '项目类型']= '部门闲置'
    res_df.loc[res_df['项目编号'].str.contains('.*-L'), '项目类型']= '部门休假'
    # res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

parser=argparse.ArgumentParser(description='加工售前、内部管理、产品研发，部门管理，部门闲置明细数据')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
parser.add_argument('--input', '-i', dest='inputfile', required=True, help='input excel file')
parser.add_argument('--output', '-o', dest='outputfile', required=True, help='output excel file')
parser.add_argument('--yyyymm', '-t', dest='yyyymm', type=str, required=True, help='输入年月yyyymm')
parser.add_argument('--projectfile', '-p', dest='projectfile', required=False, help='部门管理、闲置项目列表')
parser.add_argument('--method', '-m', dest='method', required=True, help='选择调用方法', choices=['pd_direct_cost', 'pd_manage_cost', 'pd_idle_cost'])

if __name__ == "__main__":
    # 测试用
    args=list()
    if(len(sys.argv) == 1):
        parser.print_help()
        args.append(parser.parse_args('--input F:/workspace/python/data/201812/售前、内部管理、产品研发预实对比明细表.xls --output F:/workspace/python/data/201812/非项目损益明细表-201812.xlsx -t 201812 -m pd_direct_cost'.split()))
        args.append(parser.parse_args('-p F:/workspace/python/data/201812/PROJECT-RY-201812.xlsx --input F:/workspace/python/data/201812/部门管理预实对比汇总表.xls --output F:/workspace/python/data/201812/非项目损益明细表-201812.xlsx -t 201812 -m pd_manage_cost'.split()))
        args.append(parser.parse_args('-p F:/workspace/python/data/201812/PROJECT-RY-201812.xlsx --input F:/workspace/python/data/201812/部门闲置预实对比汇总表.xls --output F:/workspace/python/data/201812/非项目损益明细表-201812.xlsx -t 201812 -m pd_idle_cost'.split()))
    else:
        args.append(parser.parse_args())

    o_file=args[0].outputfile
    writer = pd.ExcelWriter(o_file)
    
    for arg in args:
        if(arg.method == 'pd_direct_cost'):
            pd_direct_cost(arg.inputfile, 0, arg.projectfile, arg.yyyymm, writer, '售前、内部管理、产品研发', 2)
        elif(arg.method == "pd_manage_cost"):
            pd_manage_cost(arg.inputfile, 0, arg.projectfile, arg.yyyymm, writer, '部门管理', 2)
        elif(arg.method == "pd_idle_cost"):
            pd_idle_cost(arg.inputfile, 0, arg.projectfile, arg.yyyymm, writer, '部门闲置', 2)

    writer.save()
