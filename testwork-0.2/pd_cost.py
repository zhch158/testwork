# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def pd_cost(xls_file, xls_sheet=0, yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    level1=level2=level3=level4=''
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

    res_df['月份']=yyyymm
    res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    res_df['口径']='管理口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    res_df['口径']='验收口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-t --yyyymm <201812>")
    print("\t-o --output <output filename>")

def get_opts(argv):
    xls_file = ""
    xls_sheet = ""
    yyyymm = ""
    o_file = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], "hf:s:t:o:", [
                                   "help", "filename=", "sheetname=", "yyyymm=", "output="])
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
        elif opt in ("-t", "--yyyymm"):
            yyyymm = s
        elif opt in ("-o", "--output"):
            o_file = s
    if(xls_file == "" or yyyymm == "" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    if(xls_sheet == ""):
        xls_sheet=0
    return xls_file, xls_sheet, yyyymm, o_file

if __name__ == "__main__":
    # 测试用
    argv1=[]
    if(len(sys.argv) == 1):
        argv1 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201812/售前、内部管理、产品研发预实对比明细表.xls"] + ["-s"] + [""] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/非项目损益明细表.xlsx']
    else:
        argv1=sys.argv

    print("CMD:[%s]\n" % (argv1))
    xls_file, xls_sheet, yyyymm, o_file = get_opts(argv1)
    writer = pd.ExcelWriter(o_file)
    pd_cost(xls_file, xls_sheet, yyyymm, writer, '售前、内部管理、产品研发', 2)
    writer.save()
