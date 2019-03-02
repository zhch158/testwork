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
        argv1 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201811/部门损益明细表【项目】.xls"] + ['-d'] + ['验收口径'] + ['-t'] + ['201811'] + ['-o'] + ['F:/workspace/python/data/201811/项目损益明细表.xlsx']
        argv2 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201811/部门损益明细表【项目】-完工百分比法-管理口径.xls"] + ['-d'] + ['管理口径'] + ['-t'] + ['201811'] + ['-o'] + ['F:/workspace/python/data/201811/项目损益明细表.xlsx']
        argv3 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201811/部门损益明细表【项目】-完工百分比法-考核口径.xls"] + ['-d'] + ['考核口径'] + ['-t'] + ['201811'] + ['-o'] + ['F:/workspace/python/data/201811/项目损益明细表.xlsx']
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
    