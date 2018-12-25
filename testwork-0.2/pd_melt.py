# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def test_melt():
    # 伪造一些数据
    fake_data = {'subject':['math', 'english'],
                'A': [88, 90],
                'B': [70, 80],
                'C': [60, 78]}

    # 宽表
    test = pd.DataFrame(fake_data, columns=['subject', 'A', 'B', 'C'])

    # 转换为窄表
    result=pd.melt(test, id_vars=['subject'], var_name='产品名称', value_name='产品分摊比例')
    print(result)

def pd_melt(xls_file, xls_sheet=None, o_file="pp.xlsx"):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet)
    df=pd.DataFrame(data)
    result=pd.melt(df, id_vars=['项目编号', '项目名称'], var_name='产品名称', value_name='产品分摊比例')
    o_data=result.loc[result['产品分摊比例']>=0]
    o_data['调整说明']=''
    o_data.to_excel(o_file, encoding='utf-8', index=False, header=True)

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-o --output <output filename>")

def get_opts(argv):
    xls_file = ""
    xls_sheet = ""
    o_file = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], "hf:s:o:", [
                                   "help", "filename=", "sheetname=", "output="])
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
        elif opt in ("-o", "--output"):
            o_file = s
    if(xls_file == "" or xls_sheet=="" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    return xls_file, xls_sheet, o_file

if __name__ == "__main__":
    # 测试用
    if(len(sys.argv) == 1):
        sys.argv += ["-f"] + ["F:/workspace/python/data/201811/pp-20181220.xlsx"] + ["-s"] + ["PP"] + ['-o'] + ['F:/workspace/python/data/201811/pp.xlsx']
    print("CMD:[%s]\n" % (sys.argv))

    xls_file, xls_sheet, o_file = get_opts(sys.argv)
    pd_melt(xls_file, xls_sheet, o_file)
