# -*- coding: utf-8 -*-  
import sys
import pymysql
import ConfigParser

#从文件系统读取配置文件
cf = ConfigParser.ConfigParser()
cf.read("mycnf.txt")
host = cf.get("mssql", "host")
user = cf.get("mssql", "user")
pwd = cf.get("mssql", "pwd")
db = cf.get("mssql", "dbname")
 
class MSSQL:
    #def __init__(self,host=None,user=None,pwd=None,db=None):
    def __init__(self):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        
        self._conn = self.GetConnect()
        if(self._conn):
            self._cur = self._conn.cursor()
 
 
    #连接数据库
    def GetConnect(self):
        conn = False
        try:
            conn = pymssql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                database =self.db
            )
        except Exception as err:
            print("连接数据库失败, %s" % err)
        else:
            return conn
 
 
    #执行查询
    def ExecQuery(self,sql):
        res = ""
        try:
            self._cur.execute(sql)
            res = self._cur.fetchall()
        except Exception as err:
            print("查询失败, %s" % err)
        else:
            return res
 
 
    #执行非查询类语句
    def ExecNonQuery(self, sql):
        flag = False
        try:
            self._cur.execute(sql)
            self._conn.commit()
            flag = True
        except Exception as err:
            flag = False
            self._conn.rollback()
            print("执行失败, %s" % err)
        else:
            return flag
 
 
    #获取连接信息
    def GetConnectInfo(self):
        print( "连接信息：" )
        print( "服务器:%s , 用户名:%s , 数据库:%s " % (self.host,self.user,self.db))
 
 
 
    #关闭数据库连接
    def Close(self):
        if(self._conn):
            try:
                if(type(self._cur)=='object'):
                    self._cur.close()
                if(type(self._conn)=='object'):
                    self._conn.close()
            except:
                raise("关闭异常, %s,%s" % (type(self._cur), type(self._conn)))  
 
