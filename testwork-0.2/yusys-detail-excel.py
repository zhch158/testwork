#coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os,sys,getopt
import pandas as pd
import yaml
sys.path.extend([".", "../pylib"])
from utility import load_from_yaml
from pd_melt import pd_melt
from pd_filter import pd_filter
from pd_modify import pd_modify
from pd_branch import pd_branch
import pd_cost
# from pd_cost import pd_direct_cost, pd_manage_cost, pd_idle_cost

from jinja2 import Environment, FileSystemLoader, Template

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-c --config <filename>")

def get_opts(argv):
    config=""

    if(len(argv)==1):
        print_usage(argv)
        sys.exit(1)

    d_enc=sys.getdefaultencoding()
    enc=sys.getfilesystemencoding()
    print("filesystem encoding[%s], defaultencoding[%s]" %(enc, d_enc))
    try:
        opts, args = getopt.getopt(argv[1:],"hc:",["help",  "config="])
    except getopt.GetoptError:
        print_usage(argv)
        sys.exit(2)
    for opt, arg in opts:
        # s_t=arg.strip()
        # enc_t=chardet.detect(s_t)["encoding"]
        # if( enc_t!=None and "utf" in enc_t):
        #     s=s_t.decode(enc_t)
        # else:
        #     s=s_t.decode(enc)
        s=arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-c", "--config"):
            config = s
    return config

if __name__ == "__main__":
    #测试用
    workdir=''

    if(len(sys.argv)==1):
        sys.argv+=["-c"] + ["./yusys-detail-excel.yaml"]
    configfile = get_opts(sys.argv)
    config_dic=load_from_yaml(configfile)

    config=config_dic.get("config", None)
    if(config!=None):
        workdir=config.get("workdir", './')
    else:
        workdir='./'
    config['workdir']=workdir
    
    TemplateLoader = FileSystemLoader(searchpath=['.'])
    env = Environment(loader=TemplateLoader, variable_start_string='${', variable_end_string='}')
    md01 = env.get_template(configfile)
    content = md01.render(config)
    config_dic = yaml.load(content)

    pp_dict=config_dic.get("产品归属", None)
    if(pp_dict!=None):
        pp_input, pp_input_sheet=pp_dict.get("输入文件", None)
        pp_output=pp_dict.get("输出文件", None)
        print('pd_melt(xls_file=%s, xls_sheet=%s, o_file=%s)' %(pp_input, pp_input_sheet, pp_output))
        pd_melt(pp_input, pp_input_sheet, pp_output)
    
    b_dict=config_dic.get("部门列表", None)
    if(b_dict!=None):
        b_input=b_dict.get("输入文件", None)
        b_output=b_dict.get("输出文件", None)
        print('pd_branch(xls_file=%s, o_file=%s)' %(b_input, b_output))
        pd_branch(xls_file=b_input, o_file=b_output)
    
    xm_dict=config_dic.get("项目损益", None)
    if(xm_dict!=None):
        xm_list=xm_dict.get("输入文件", None)
        xm_output=xm_dict.get("输出文件", None)
        xm_yyyymm=xm_dict.get("月份", None)
        writer = pd.ExcelWriter(xm_output)
        for xm_input, methods, skiprows in xm_list:
            print("pd_mdify(xls_file=%s, methods=%s, yyyymm=%s, o_file=%s, skiprows=%d)" 
                %(xm_input, methods, xm_yyyymm, xm_output, skiprows))
            pd_modify(xls_file=xm_input, methods=methods, yyyymm=xm_yyyymm, o_file=writer, skiprows=skiprows)
        writer.save()
    
    fxm_dict=config_dic.get("非项目损益", None)
    if(fxm_dict!=None):
        fxm_list=fxm_dict.get("输入文件", None)
        fxm_output=fxm_dict.get("输出文件", None)
        fxm_branch=fxm_dict.get("部门列表", None)
        fxm_yyyymm=fxm_dict.get("月份", None)
        writer = pd.ExcelWriter(fxm_output)
        for fxm_input, o_sheet, skiprows in fxm_list:
            print('pd_mdify(xls_file=%s, xls_branch=%s, yyyymm=%s, o_file=%s, o_sheet=%s, skiprows=%d)' 
                %(fxm_input, fxm_branch, fxm_yyyymm, fxm_output, o_sheet, skiprows))
            pd_filter(xls_file=fxm_input, xls_branch=fxm_branch, yyyymm=fxm_yyyymm, o_file=writer, o_sheet=o_sheet, skiprows=skiprows)
        writer.save()
    
    fxm_dict=config_dic.get("非项目费用", None)
    if(fxm_dict!=None):
        fxm_list=fxm_dict.get("输入文件", None)
        fxm_output=fxm_dict.get("输出文件", None)
        fxm_yyyymm=fxm_dict.get("月份", None)
        writer = pd.ExcelWriter(fxm_output)
        for fxm_func, fxm_input, o_sheet, skiprows in fxm_list:
            print('pd_mdify(func=%s, xls_file=%s, yyyymm=%s, o_file=%s, o_sheet=%s, skiprows=%d)' 
                %(fxm_func, fxm_input, fxm_yyyymm, fxm_output, o_sheet, skiprows))
            func=getattr(pd_cost, fxm_func, None)
            if(func==None):
                print('Func{%s] is not found' %(fxm_func))
                continue
            func(xls_file=fxm_input, yyyymm=fxm_yyyymm, o_file=writer, o_sheet=o_sheet, skiprows=skiprows)
        writer.save()
    