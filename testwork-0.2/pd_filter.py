# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def pd_filter(xls_file, xls_sheet=0, xls_branch='部门列表.xls', yyyymm='201801', o_file="result.xlsx", o_sheet='立项'):
    level1=level2=level3=level4=''
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=2, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['项目类型', '实施部门', '项目编号', '项目名称', '项目状态', '成本分类', '总成本']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))

    branch=pd.read_excel(xls_branch, sheet_name=0)

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    # sub_df0=df.loc[df['成本分类']=='本月累计']
    # sub_df1=df.loc[df['成本分类']=='本年累计']
    i=0
    for index,row in df.iterrows():
        # print(index)
        # print(row)
        if(index==0 or index == 1):
            continue
        if(index%2==0):
            row_0=row
        else:
            if(row['成本分类']=='本年累计'):
                cost=row['总成本']
            else:
                cost=row_0['总成本']
            branch_row=branch.loc[branch['部门']==row_0['实施部门']]
            if(branch_row.size==0):
                level1=level2=level3=level4=''
                print('部门[%s] 部门列表中不存在' %(row_0['实施部门']))
            else:
                level1, level2, level3, level4=branch_row.values[0][1:5]
            res_df.loc[i]=[yyyymm, row_0['项目类型'], row_0['项目编号'], row_0['项目名称'], row_0['项目状态'], 
                level1, level2, level3, level4, cost, cost, '考核口径']
            # res_row=pd.Series(['201811', row_0['项目类型'], row_0['项目编号'], row_0['项目名称'], row_0['项目状态'], level1, level2, level3, level4, row['总成本'], row['总成本'], '考核口径'])
            # res_df.append(res_row, ignore_index=True)
            i+=1
    
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    res_df['口径']='管理口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    res_df['口径']='验收口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

    # o_data['调整说明']=''
    # o_data.to_excel(o_file, encoding='utf-8', index=False, header=True)

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-b --branchfile <execl filename>")
    print("\t-t --yyyymm <201811>")
    print("\t-o --output <output filename>")

def get_opts(argv):
    xls_file = ""
    xls_sheet = ""
    xls_branch = ""
    yyyymm = ""
    o_file = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], "hf:s:b:t:o:", [
                                   "help", "filename=", "sheetname=", "branchfile=", "yyyymm=", "output="])
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
        elif opt in ("-b", "--branchfile"):
            xls_branch = s
        elif opt in ("-t", "--yyyymm"):
            yyyymm = s
        elif opt in ("-o", "--output"):
            o_file = s
    if(xls_file == "" or xls_branch == "" or yyyymm == "" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    if(xls_sheet == ""):
        xls_sheet=0
    return xls_file, xls_sheet, xls_branch, yyyymm, o_file

if __name__ == "__main__":
    # 测试用
    argv1=[]
    argv2=[]
    if(len(sys.argv) == 1):
        argv1 += [sys.argv[0]] + ["-f"] + ["成本明细表【非项目-不立项】.xls"] + ["-s"] + [""] + ['-b'] + ['部门列表.xls'] + ['-t'] + ['201811'] + ['-o'] + ['非项目损益明细表.xlsx']
        argv2 += [sys.argv[0]] + ["-f"] + ["成本明细表【非项目-立项】.xls"] + ['-b'] + ['部门列表.xls'] + ['-t'] + ['201811'] + ['-o'] + ['非项目损益明细表.xlsx']
    else:
        argv1=sys.argv

    print("CMD:[%s]\n" % (argv1))
    xls_file, xls_sheet, xls_branch, yyyymm, o_file = get_opts(argv1)
    writer = pd.ExcelWriter(o_file)
    pd_filter(xls_file, xls_sheet, xls_branch, yyyymm, writer, '不立项')

    print("CMD:[%s]\n" % (argv2))
    xls_file, xls_sheet, xls_branch, yyyymm, o_file = get_opts(argv2)
    pd_filter(xls_file, xls_sheet, xls_branch, yyyymm, writer, '立项')

    writer.save()
