# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import pandas as pd

def set_value(name, prefix='', suffix=''):
    return prefix + name + suffix

def pd_direct_cost(xls_file, xls_sheet=0, yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
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
    res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    res_df['口径']='管理口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    res_df['口径']='验收口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

def pd_manage_cost(xls_file, xls_sheet=0, yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['所属一级部', '所属二级部', '部门总累计实际数  ']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df=df.fillna(method='ffill')
    df=df.loc[df['所属二级部'].str.contains('汇总', regex=True)==False]

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    res_df['所属部门级一']=df['所属一级部']
    res_df['所属部门级二']=df['所属二级部']
    res_df['项目编号']=df['所属二级部'].apply(lambda x: set_value(x, 'YTEC-2019-', '-W'))
    res_df['项目名称']=df['所属二级部'].apply(lambda x:set_value(x, suffix='-部门管理'))
    res_df['累计总成本']=df['部门总累计实际数  ']
    res_df['当年累计成本']=df['部门总累计实际数  ']

    res_df['月份']=yyyymm
    res_df['项目类型']='部门管理'
    res_df['项目状态']='考勤报工'
    res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    res_df['口径']='管理口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    res_df['口径']='验收口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

def pd_idle_cost(xls_file, xls_sheet=0, yyyymm='201801', o_file="result.xlsx", o_sheet='立项', skiprows=2):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet, skiprows=skiprows, skipfooter=0)
    df=pd.DataFrame(data).loc[:, ['一级部名称', '二级部名称', '累计至今部门闲置实际支出']]
    print("file[%s], rows[%d], cols[%d]" %(xls_file, df.iloc[:,0].size, df.columns.size))
    df=df.fillna(method='ffill')
    df=df.loc[df['二级部名称'].str.contains('汇总', regex=True)==False]

    res_df=pd.DataFrame(columns=['月份', '项目类型', '项目编号', '项目名称', '项目状态', '所属部门级一', '所属部门级二', '所属部门级三', '所属部门级四', '累计总成本', '当年累计成本', '口径'])
    res_df['所属部门级一']=df['一级部名称']
    res_df['所属部门级二']=df['二级部名称']
    res_df['项目编号']=df['二级部名称'].apply(lambda x: set_value(x, 'YTEC-2019-', '-Y'))
    res_df['项目名称']=df['二级部名称'].apply(lambda x:set_value(x, suffix='-部门闲置'))
    res_df['累计总成本']=df['累计至今部门闲置实际支出']
    res_df['当年累计成本']=df['累计至今部门闲置实际支出']

    res_df['月份']=yyyymm
    res_df['项目类型']='部门闲置'
    res_df['项目状态']='考勤报工'
    res_df['口径']='考核口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'考核', index=False, header=True)

    res_df['口径']='管理口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'管理', index=False, header=True)

    res_df['口径']='验收口径'
    res_df.to_excel(o_file, encoding='utf-8', sheet_name=o_sheet+'-'+'验收', index=False, header=True)

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-[d|m|i] --[direct|manage|idle]")
    print("\t-f --filename <execl filename>")
    print("\t-s --sheetname <execl sheetname>")
    print("\t-t --yyyymm <201812>")
    print("\t-o --output <output filename>")

def get_opts(argv):
    xls_type = ""
    xls_file = ""
    xls_sheet = ""
    yyyymm = ""
    o_file = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], "hdmif:s:t:o:", [
                                   "help", "direct", "manage", "idle", "filename=", "sheetname=", "yyyymm=", "output="])
    except getopt.GetoptError:
        print_usage(argv)
        sys.exit(2)
    for opt, arg in opts:
        s = arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        if opt in ("-d", "--direct"):
            xls_type='-d'
        if opt in ("-m", "--manage"):
            xls_type='-m'
        if opt in ("-i", "--idle"):
            xls_type='-i'
        elif opt in ("-f", "--filename"):
            xls_file = s
        elif opt in ("-s", "--sheetname"):
            xls_sheet = s
        elif opt in ("-t", "--yyyymm"):
            yyyymm = s
        elif opt in ("-o", "--output"):
            o_file = s
    if(xls_type == "" or xls_file == "" or yyyymm == "" or o_file==""):
        print_usage(argv)
        sys.exit(3)
    if(xls_sheet == ""):
        xls_sheet=0
    return xls_type, xls_file, xls_sheet, yyyymm, o_file

if __name__ == "__main__":
    # 测试用
    argv1=[]
    if(len(sys.argv) == 1):
        #argv1 += [sys.argv[0]] + ["-d"] + ["-f"] + ["F:/workspace/python/data/201812/售前、内部管理、产品研发预实对比明细表.xls"] + ["-s"] + [""] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/非项目损益明细表.xlsx']
        #argv1 += [sys.argv[0]] + ["-m"] + ["-f"] + ["F:/workspace/python/data/201812/部门管理预实对比汇总表.xls"] + ["-s"] + [""] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/非项目损益明细表.xlsx']
        argv1 += [sys.argv[0]] + ["-i"] + ["-f"] + ["F:/workspace/python/data/201812/部门闲置预实对比汇总表.xls"] + ["-s"] + [""] + ['-t'] + ['201812'] + ['-o'] + ['F:/workspace/python/data/201812/非项目损益明细表.xlsx']
    else:
        argv1=sys.argv

    print("CMD:[%s]\n" % (argv1))
    xls_type, xls_file, xls_sheet, yyyymm, o_file = get_opts(argv1)
    writer = pd.ExcelWriter(o_file)
    
    if(xls_type == "-d"):
        pd_direct_cost(xls_file, xls_sheet, yyyymm, writer, '售前、内部管理、产品研发', 2)
    elif(xls_type == "-m"):
        pd_manage_cost(xls_file, xls_sheet, yyyymm, writer, '部门管理', 2)
    elif(xls_type == "-i"):
        pd_idle_cost(xls_file, xls_sheet, yyyymm, writer, '部门闲置', 2)

    writer.save()
