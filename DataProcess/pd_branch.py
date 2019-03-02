# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def pd_branch(xls_file, xls_sheet=0, o_file="branch.xlsx"):
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
    if(xls_file == "" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    if(xls_sheet == ""):
        xls_sheet=0
    return xls_file, xls_sheet, o_file

if __name__ == "__main__":
    # 测试用
    argv1=[]
    if(len(sys.argv) == 1):
        argv1 += [sys.argv[0]] + ["-f"] + ["F:/workspace/python/data/201811/执行中组织结构基本信息表 20181225130600.xlsx"] + ['-o'] + ['F:/workspace/python/data/201811/部门列表-201812.xlsx']
    else:
        argv1=sys.argv

    print("CMD:[%s]\n" % (argv1))
    xls_file, xls_sheet, o_file = get_opts(argv1)
    pd_branch(xls_file, xls_sheet, o_file)
