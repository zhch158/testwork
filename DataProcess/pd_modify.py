# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
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

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-t --yyyymm <201811>")
    print("\t-d --methods <考核口径>")
    print("\t-o --output <output filename>")

def get_opts(argv):
    xls_file = ""
    xls_sheet = ""
    methods = ""
    yyyymm = ""
    o_file = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], "hf:s:d:t:o:", [
                                   "help", "filename=", "sheetname=", "methods=", "yyyymm=", "output="])
    except getopt.GetoptError:
        print_usage(argv)
        sys.exit(2)
    for opt, arg in opts:
        s = arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-f", "--filename"):
            xls_file = s
        elif opt in ("-s", "--sheetname"):
            xls_sheet = s
        elif opt in ("-d", "--methods"):
            methods = s
        elif opt in ("-t", "--yyyymm"):
            yyyymm = s
        elif opt in ("-o", "--output"):
            o_file = s
    if(xls_file == "" or methods == "" or yyyymm == "" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    if(xls_sheet == ""):
        xls_sheet=0
    return xls_file, xls_sheet, methods, yyyymm, o_file

if __name__ == "__main__":
    # 测试用
    argv1=[]
    argv2=[]
    argv3=[]
    if(len(sys.argv) == 1):
        argv1 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201812/部门损益明细表【项目】.xls"] + ['-d'] + ['验收口径'] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/项目损益明细表-201812.xlsx']
        argv2 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201812/部门损益明细表【项目】-完工百分比法-管理口径.xls"] + ['-d'] + ['管理口径'] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/项目损益明细表-201812.xlsx']
        argv3 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201812/部门损益明细表【项目】-完工百分比法-考核口径.xls"] + ['-d'] + ['考核口径'] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/项目损益明细表-201812.xlsx']
    else:
        argv1=sys.argv

    print("\nCMD:[%s]\n" % (argv1))
    xls_file, xls_sheet, methods, yyyymm, o_file = get_opts(argv1)

    writer = pd.ExcelWriter(o_file)

    pd_modify(xls_file, xls_sheet, methods, yyyymm, writer, 2)

    print("\nCMD:[%s]\n" % (argv2))
    xls_file, xls_sheet, methods, yyyymm, o_file = get_opts(argv2)
    pd_modify(xls_file, xls_sheet, methods, yyyymm, writer, 3)

    print("\nCMD:[%s]\n" % (argv3))
    xls_file, xls_sheet, methods, yyyymm, o_file = get_opts(argv3)
    pd_modify(xls_file, xls_sheet, methods, yyyymm, writer, 3)

    writer.save()
    