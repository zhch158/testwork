# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import argparse
import pandas as pd

class Db:
    def __init__(self):
        pass
    sysName = ""
    dataDt = ""
    #userName
    loginUsr = ""
    #密码
    loginPwd = ""
    #数据库SID或者IP
    dbName = ""
    #数据库连接串
    connStr = ""
    #判断参数输入是否正确
    def get_param(self):
        #判断输入参数数量是否匹配
        if len(sys.argv) != 3:
           print("ERROR:输入格式为： 系统简称  跑批日期")
           print("ERROR:参数不符")
           sys.exit(1)
        #声明使用全局变量
        global sysName,dataDt
        sysName= sys.argv[1].upper()
        dataDt = sys.argv[2]
        #判断输入日期是否规范
        if len(dataDt) != 8:
            print("ERROR:日期格式不对，需要输入'20180101'格式日期！")
            sys.exit(2)

    #获取卸数系统的数据库账号密码，sid
    def get_db(self):
        global logInfo
        logInfo = common.Log_Set('bdp',dataDt,'etl_run_date').logger_set()
        mysqlResult = common.Get_Dbinfo("BDP_PARAM").get_param_byini("mysql")
        global dbName,loginUsr,loginPwd,connStr
        dbName = mysqlResult[0]
        loginUsr = mysqlResult[1]
        loginPwd = mysqlResult[2]
        connStr = "DSN="+dbName+";UID="+loginUsr+";PWD="+loginPwd
        logInfo.info("-------进入翻牌作业----------")

    #连接数据库,执行SQL(INSERT,UPDATE,TRUNCATE,DELETE)
    def con_db_execsql(self,execSql):
        try:
            #连接数据库
            conDb = pyodbc.connect(connStr)
            cursorDb = conDb.cursor()
            execResult = cursorDb.execute(execSql).rowcount
            logInfo.info(execSql)
            cursorDb.commit()
            cursorDb.close()
            conDb.close()
            return execResult
        except Exception as e:
            logInfo.error(e)
            exit(3)

    #连接数据库,执行SELECT SQL获取结果集
    def con_db_selcsql(self,selcSql):
        try:
            #连接数据库
            conDb = pyodbc.connect(connStr)
            cursorDb = conDb.cursor()
            #获取数据表结构,用于拼接select语句
            executeSql = cursorDb.execute(selcSql)
            logInfo.info(selcSql)
            sqlResults = executeSql.fetchall()
            cursorDb.close()
            conDb.close()
            return sqlResults
        except Exception as e:
            logInfo.error(e)
            exit(4)

    def bdp_next_day(self):
        #生成翻牌语句
        #updateinfo = "UPDATE BDP_ETL_RUN_DATE SET SYS_DATE=DATE_FORMAT(DATE_SUB(STR_TO_DATE(sys_date,'%Y%m%d'),INTERVAL -1 DAY),'%Y%m%d') WHERE SYS_TYPE='"+sysName+"'"
        #5fb697692c1e4351ba1c535dfd46913c为日历表中工作日/交易日日历的ID
        nextDt = ""
        selecNextTx = "select min(a.date_value) from use_calendar_data a where a.app_code='BDP' and calendar_code='5fb697692c1e4351ba1c535dfd46913c' and a.type_code='1' and a.date_value>'"+dataDt+"'"
        nextDtResults = self.con_db_selcsql(selecNextTx)
        if(nextDtResults == []):
            logInfo.error("无法获取下一个工作日")
            exit(4)
        for nextResult in nextDtResults:
            print("row="+str(nextResult[0]))
            logInfo.info("作业翻牌日期为："+str(nextResult[0]))
            nextDt = nextResult[0]

        updateinfo = "UPDATE BDP_ETL_RUN_DATE SET SYS_DATE='"+nextDt+"' WHERE SYS_TYPE='"+sysName+"'"
        logInfo.info("更新语句为："+updateinfo)
        execResult = self.con_db_execsql(updateinfo)
        logInfo.info("-------执行作业翻牌----------pnext="+str(execResult))
        print("pnext="+str(execResult))
        #生成检查语句
        selectinfo = "SELECT SYS_DATE FROM BDP_ETL_RUN_DATE WHERE SYS_TYPE='"+sysName+"'"
        logInfo.info("检查更新结果语句为："+selectinfo)
        selcResult = self.con_db_selcsql(selectinfo)
        print ("检查更新结果语句为："+selectinfo)
        if(selcResult == []):
            logInfo.error("无法获取表信息")
            insSql = "INSERT INTO BDP_ETL_RUN_DATE(sys_type,sys_date,sys_status) values('"+sysName+"','"+nextDt+"','Y')"
            execResult = self.con_db_execsql(insSql)
        for row in selcResult:
            print("row="+str(row[0]))
            logInfo.info("作业翻牌日期为："+str(row[0]))
        logInfo.info("作业执行完成")
    #主函数
    def Main(self):
        #获取该数据库信息
        self.get_db()
        #根据报错作业分析出后续依赖作业生成作业流配置表
        self.bdp_next_day()

def sync_pp(xls_file, xls_sheet=None, dbcursor):
    data=pd.read_excel(xls_file, sheet_name=xls_sheet)
    df=pd.DataFrame(data)
    result=pd.melt(df, id_vars=['项目编号', '项目名称'], var_name='产品名称', value_name='产品分摊比例')
    #删除空行
    result.dropna(axis=1)
    result['调整说明']=pd.np.nan
    # result=result.loc[result['产品分摊比例'].astype('str')!=None]
    # o_data=result.loc[result['产品分摊比例'].astype('int')>=0]
    # o_data=result.loc[result['产品分摊比例']>=0]
    o_data=result.loc[result['产品分摊比例'].astype('float')>=0]
    o_data.to_excel(o_file, encoding='utf-8', index=False, header=True)