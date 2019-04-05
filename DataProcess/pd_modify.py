# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
# 根据项目损益明细表（考核，管理，验收），生成项目各口径的明细数据
import os
import sys
import argparse
import getopt
import pandas as pd

def pd_modify(xls_file, xls_sheet=0, methods='考核口径', yyyymm='201801', o_file="result.xlsx", skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))

    df.rename(columns={'序号': '月份'}, inplace=True)
    df['月份']=yyyymm
    df['口径']=methods

    if(methods=='验收口径'):
        res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '项目结项状态', '项目结项时间', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '内部订单编号', '内部订单状态', '合同编号', '原合同编号', '合同签订状态', '项目实施金额', '项目实施金额（脱税）', '项目当前预算利润率', '历年累计确认收入(含税)', '历年累计确认收入(脱税)', '历年累计利润', '历年累计利润率(含税)', '历年累计税金', '收入截止确认月份', '当年累计收入(含税)', '当年累计收入(脱税)', '当年累计成本', '当年累计利润', '当年累计利润率(含税)', '当年累计税金', '待结转收入(含税)', '客户名称(全称)', '大客户类型', '口径'])
        res_df['项目编号']=df['项目编号']
        res_df['项目名称']=df['项目名称']
        res_df['项目类型']=df['项目类型']
        res_df['项目状态']=df['项目状态']
        res_df['项目结项状态']=df['项目结项状态']
        res_df['项目结项时间']=df['项目结项时间']
        res_df['所属部门级一']=df['所属部门级四']
        res_df['所属部门级二']=df['所属部门级三']
        res_df['所属部门级三']=df['所属部门级二']
        res_df['所属部门级四']=df['所属部门级一']
        res_df['内部订单编号']=df['内部订单编号']
        res_df['内部订单状态']=df['内部订单状态']
        res_df['合同编号']=df['合同编号']
        res_df['合同签订状态']=df['合同签订状态']
        res_df['项目当前预算利润率']=df['预算毛利率（税后）']
        res_df['当年累计收入(脱税)']=df['当年累计收入(脱税)']
        res_df['当年累计成本']=df['当年累计成本']
        res_df['当年累计利润']=df['当年累计利润']
        res_df['客户名称(全称)']=df['客户名称(全称)']
        res_df['月份']=df['月份']
        res_df['口径']=df['口径']
        res_df.to_excel(o_file, encoding='utf-8', sheet_name=methods, index=False, header=True)
    else:
        df.to_excel(o_file, encoding='utf-8', sheet_name=methods, index=False, header=True)

def pd_check(xls_file, xls_sheet, yyyymm, o_file, skiprows=3):
    return pd_modify(xls_file, xls_sheet, '考核口径', yyyymm, o_file, skiprows)

def pd_manage(xls_file, xls_sheet, yyyymm, o_file, skiprows=3):
    return pd_modify(xls_file, xls_sheet, '管理口径', yyyymm, o_file, skiprows)

def pd_receive(xls_file, xls_sheet, yyyymm, o_file, skiprows=2):
    return pd_modify(xls_file, xls_sheet, '验收口径', yyyymm, o_file, skiprows)

parser=argparse.ArgumentParser(description='加工项目损益明细')
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--mode', '-m', dest='mode', nargs=1, choices=['sum', 'max'], required=True, help='input mode')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
parser.add_argument('--input', '-i', dest='inputfile', required=True, help='input excel file')
parser.add_argument('--output', '-o', dest='outputfile', required=True, help='output excel file')
parser.add_argument('--yyyymm', '-t', dest='yyyymm', type=str, required=True, help='输入年月yyyymm')
parser.add_argument('--method', '-m', dest='method', required=True, help='选择调用方法', choices=['pd_check', 'pd_manage', 'pd_receive'])

if __name__ == "__main__":
    # 测试用
    args=list()
    if(len(sys.argv) == 1):
        parser.print_help()
        args.append(parser.parse_args('--input F:/workspace/python/data/201812/部门损益明细表【项目】.xls --output F:/workspace/python/data/201812/项目损益明细表-201812.xlsx -t 201812 -m pd_receive'.split()))
        args.append(parser.parse_args('--input F:/workspace/python/data/201812/部门损益明细表【项目】-完工百分比法-管理口径.xls --output F:/workspace/python/data/201812/项目损益明细表-201812.xlsx -t 201812 -m pd_manage'.split()))
        args.append(parser.parse_args('--input F:/workspace/python/data/201812/部门损益明细表【项目】-完工百分比法-考核口径.xls --output F:/workspace/python/data/201812/项目损益明细表-201812.xlsx -t 201812 -m pd_check'.split()))
    else:
        args.append(parser.parse_args())

    o_file=''
    writer=None
    for arg in args:
        if(arg.outputfile!=o_file):
            if(writer):
                writer.save()
            o_file=arg.outputfile
            writer = pd.ExcelWriter(o_file)
        func=globals().get(arg.method)
        if(func!=None):
            func(arg.inputfile, 0, arg.yyyymm, writer)
        else:
            raise("find function[{}] error".format(arg.method))  

    writer.save()    
