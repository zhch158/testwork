# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def pd_workload(xls_file, xls_sheet=0, yyyymm='201801', o_file="result.xlsx", skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data)
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df=df.loc[df['项目编号'].notna()]

    df.insert(0, '月份', yyyymm)
    df.to_excel(o_file, encoding='utf-8', sheet_name=str(yyyymm), index=False, header=True)

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-t --yyyymm <201811>")
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
        argv1 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201812/项目人工投入统计表(按人员-项目).xls"] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/项目人工投入统计表(按人员-项目)-201812.xlsx']
    else:
        argv1=sys.argv

    print("\nCMD:[%s]\n" % (argv1))
    xls_file, xls_sheet, yyyymm, o_file = get_opts(argv1)

    writer = pd.ExcelWriter(o_file)

    pd_workload(xls_file, xls_sheet, yyyymm, writer, 2)

    writer.save()
    