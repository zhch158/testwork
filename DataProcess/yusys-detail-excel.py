#coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os,sys
import argparse
import pandas as pd
import yaml
sys.path.extend([".", "../pylib"])
from utility import load_from_yaml
from op_mysql import PdMysql, Mysql, get_db_conf
from pd_melt import pd_melt
from pd_dict import pd_project
import pd_delivery
import pd_cost
import pd_sync_db
import pd_update_db

from jinja2 import Environment, FileSystemLoader, Template

if __name__ == "__main__":
    # 测试用
    parser=argparse.ArgumentParser(description='根据配置文件，加工明细数据，同步、修改数据库')
    parser.add_argument('--config', '-c', dest='inputfile', required=True, help='input config file')
    parser.add_argument('--section', '-s', dest='section', required=False, help='input section')
    parser.add_argument('--workdir', '-w', dest='workdir', required=False, help='input workdir')
    parser.add_argument('--yyyymm', '-d', dest='yyyymm', type=str, required=False, help='input year month[201901]')

    # parser.print_help()

    pp_dict=workload_dict=b_dict=xm_dict=fxm_dict=sync_dict=upd_dict=None
    workdir=yyyymm=None

    if(len(sys.argv) == 1):
        # parser.print_help()
        args=parser.parse_args('--config ./yusys-detail-excel.yaml'.split())
        # args=parser.parse_args('--yyyymm 201901 --config ./yusys-detail-excel.yaml --section 项目人工投入'.split())
        # args=parser.parse_args('--workdir F:/workspace/python/data --yyyymm 201901 --config ./yusys-detail-excel.yaml --section 非项目费用'.split())
    else:
        args=parser.parse_args()

    configfile = args.inputfile
    workdir=args.workdir
    yyyymm=args.yyyymm

    config_dic=load_from_yaml(configfile)

    config=config_dic.get("config", None)
    if(workdir==None):
        if(config!=None):
            workdir=config.get("workdir", './')
        else:
            workdir='./'
    config['workdir']=workdir
    if(yyyymm!=None):
        config['yyyymm']=yyyymm
    
    TemplateLoader = FileSystemLoader(searchpath=['.'])
    env = Environment(loader=TemplateLoader, variable_start_string='${', variable_end_string='}')
    md01 = env.get_template(configfile)
    content = md01.render(config)
    config_dic = yaml.load(content)

    section_name=args.section

    if(section_name==None or section_name=="产品归属"):
        pp_dict=config_dic.get("产品归属", None)
        if(pp_dict!=None):
            pp_input, pp_input_sheet=pp_dict.get("输入文件", None)
            pp_output=pp_dict.get("输出文件", None)
            print('pd_melt(xls_file=%s, xls_sheet=%s, o_file=%s)' %(pp_input, pp_input_sheet, pp_output))
            pd_melt(pp_input, pp_input_sheet, pp_output)
    
    if(section_name==None or section_name=="项目人工投入"):
        workload_dict=config_dic.get("项目人工投入", None)
        if(workload_dict!=None):
            workload_list=workload_dict.get("输入文件", None)
            workload_output=workload_dict.get("输出文件", None)
            workload_yyyymm=workload_dict.get("月份", None)
            writer = pd.ExcelWriter(workload_output)
            for workload_func, workload_input, skiprows in workload_list:
                print('pd_cost(func=%s, xls_file=%s, yyyymm=%s, o_file=%s, skiprows=%d)' 
                    %(workload_func, workload_input, workload_yyyymm, workload_output, skiprows))
                func=getattr(pd_cost, workload_func, None)
                if(func==None):
                    print('Func{%s] is not found' %(workload_func))
                    continue
                func(xls_file=workload_input, yyyymm=workload_yyyymm, o_file=writer, skiprows=skiprows)
            writer.save()
    
    if(section_name==None or section_name=="非立项项目列表"):
        b_dict=config_dic.get("非立项项目列表", None)
        if(b_dict!=None):
            db_params=get_db_conf(config['dbconfig'])
            pdConn = PdMysql(**db_params)
            b_output=b_dict.get("输出文件", None)
            print('pd_project(o_file=%s)' %(b_output))
            pd_project(pdConn.engine, o_file=b_output)
    
    if(section_name==None or section_name=="项目损益"):
        xm_dict=config_dic.get("项目损益", None)
        if(xm_dict!=None):
            xm_list=xm_dict.get("输入文件", None)
            xm_output=xm_dict.get("输出文件", None)
            xm_yyyymm=xm_dict.get("月份", None)
            writer = pd.ExcelWriter(xm_output)
            for xm_func, xm_input, skiprows in xm_list:
                print("pd_delivery(func=%s, xls_file=%s, yyyymm=%s, o_file=%s, skiprows=%d)" 
                    %(xm_func, xm_input, xm_yyyymm, xm_output, skiprows))
                func=getattr(pd_delivery, xm_func, None)
                if(func==None):
                    print('Func{%s] is not found' %(xm_func))
                    continue
                func(xls_file=xm_input, yyyymm=xm_yyyymm, o_file=writer, skiprows=skiprows)
            writer.save()
    
    if(section_name==None or section_name=="非项目费用"):
        fxm_dict=config_dic.get("非项目费用", None)
        if(fxm_dict!=None):
            fxm_list=fxm_dict.get("输入文件", None)
            fxm_output=fxm_dict.get("输出文件", None)
            fxm_yyyymm=fxm_dict.get("月份", None)
            fxm_project=fxm_dict.get("非立项项目列表", None)
            writer = pd.ExcelWriter(fxm_output)
            for fxm_func, fxm_input, skiprows in fxm_list:
                print('pd_cost(func=%s, xls_file=%s, xls_project=%s, yyyymm=%s, o_file=%s, skiprows=%d)' 
                    %(fxm_func, fxm_input, fxm_project, fxm_yyyymm, fxm_output, skiprows))
                func=getattr(pd_cost, fxm_func, None)
                if(func==None):
                    print('Func{%s] is not found' %(fxm_func))
                    continue
                func(xls_file=fxm_input, xls_project=fxm_project, yyyymm=fxm_yyyymm, o_file=writer, skiprows=skiprows)
            writer.save()
    
    if(section_name==None or section_name=="同步数据库"):
        sync_dict=config_dic.get("同步数据库", None)
        if(sync_dict!=None):
            db_params=get_db_conf(config['dbconfig'])
            pdConn = PdMysql(**db_params)
            sync_list=sync_dict.get("输入文件", None)
            sync_yyyymm=sync_dict.get("月份", None)
            for sync_func, sync_input, sync_table in sync_list:
                print('pd_sync_db(func=%s, xls_file=%s, yyyymm=%s, table=%s)' 
                    %(sync_func, sync_input, sync_yyyymm, sync_table))
                func=getattr(pd_sync_db, sync_func, None)
                if(func==None):
                    print('Func{%s] is not found' %(sync_func))
                    continue
                func(pdConn.engine, tablename=sync_table, xls_file=sync_input, yyyymm=sync_yyyymm)
    
    if(section_name==None or section_name=="调整数据库"):
        upd_dict=config_dic.get("调整数据库", None)
        if(upd_dict!=None):
            db_params=get_db_conf(config['dbconfig'])
            mydb = Mysql(**db_params)
            upd_list=upd_dict.get("输入文件", None)
            upd_yyyymm=upd_dict.get("月份", None)
            for upd_func in upd_list:
                print('pd_update_db(func=%s, yyyymm=%s)' %(upd_func, upd_yyyymm))
                func=getattr(pd_update_db, upd_func, None)
                if(func==None):
                    print('Func{%s] is not found' %(upd_func))
                    continue
                try:
                    func(mydb, yyyymm=upd_yyyymm)
                    mydb.commit()
                except:
                    mydb.rollback()
            #关闭数据库
            mydb.close()
