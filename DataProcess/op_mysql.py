# -*- coding: utf-8 -*-  
import sys
import pymysql
# import mysql.connector
import configparser

def get_db_conf(configfile, dbtype='mysql'):
    #从文件系统读取配置文件
    cf = configparser.ConfigParser()
    cf.read(configfile)
    host = cf.get(dbtype, "host")
    port = cf.get(dbtype, "port")
    user = cf.get(dbtype, "user")
    pwd = cf.get(dbtype, "password")
    db = cf.get(dbtype, "database")
    db_params={'host':host, 'port':port, 'username':user, 'password':pwd, 'database':db}
    return db_params

class Mysql:
    # def __init__(self):

    # cursorclass = pymysql.cursors.DictCursor
    def __init__(self, host="127.0.0.1", port="3306", 
        username="root", password="root", database="test", charset='utf8', cursorclass = pymysql.cursors.Cursor):
        '''类例化，处理一些连接操作'''
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = int(port)
        self.charset=charset
        self.cursorclass=cursorclass

        self.cur = None
        self.con = None
        # connect to mysql
        try:
            self.con = pymysql.connect(host = self.host, user = self.username, password = self.password, port = self.port, 
                database = self.database, charset=self.charset, cursorclass = self.cursorclass)
            self.cur = self.con.cursor()
        except Exception as e:
            print('connect error [%s]' %e)
            raise("DataBase connect error,please check the db config")  

    def create_table(self,sql_str):
        '''创建数据表'''
        try:
            self.cur.execute(sql_str)
        except Exception as e:
            print(e)

    def select_sql_dict(self,sql_str, args=None):
        '''查询数据，返回一个列表，里面的每一行是一个字典，带字段名
            cursor 为连接光标
            sql_str为查询语句
        '''
        try:
            self.cur.execute(sql_str, args)
            rows = self.cur.fetchall()
            column_names=[]
            for col in self.cur.description:
                column_names.append(col[0])
            r = []
            for x in rows:
                r.append(dict(zip(column_names,x)))
            return r
        except Exception as e:
            print(e)
            raise e

    def select_sql(self,sql_str, args=None):
        '''查询数据并返回
             cursor 为连接光标
             sql_str为查询语句
        '''
        try:
            self.cur.execute(sql_str, args)
            rows = self.cur.fetchall()
            return rows
        except Exception as e:
            print(e)
            raise e

    def execute_sql(self, sql, args=None):
        '''
        插入或更新记录 成功返回受影响的行数
        '''
        try:
            num=self.cur.execute(sql, args)
            self.con.commit()
            return num
        except Exception as e:
            print(e)
            raise e
 
    #关闭数据库连接
    def close(self):
        if(self.con):
            try:
                if(type(self.cur)=='object'):
                    self.cur.close()
                if(type(self.con)=='object'):
                    self.con.close()
            except:
                raise("关闭异常, %s,%s" % (type(self.cur), type(self.con)))  
 
    #获取连接信息
    def get_connect_info(self):
        print( "连接信息：" )
        print( "服务器:%s , 用户名:%s , 数据库:%s " % (self.host,self.username,self.database))
 
if __name__ == "__main__":
    #从文件系统读取配置文件
    db_params=get_db_conf('database.ini')

    mydb = Mysql(**db_params)
    # mydb = Mysql(db_params, cursorclass='pymysql.cursors.DictCursor')
    #创建表
    mydb.create_table('create table user (id varchar(20) primary key, name varchar(20))')
    #插入数据
    # mydb.execute_sql("insert into user (id, name) values  ('1', 'Michael')")
    # 查询数据表
    results = mydb.select_sql("SELECT * FROM user")
    print(results)
    for row in results:
        id = row[0]
        name = row[1]
        print("id=%s,name=%s" %(id, name))
    list = mydb.select_sql_dict("SELECT * FROM user")
    for i in list:
        print ("记录号：%s   值：%s" % (list.index(i) + 1, i))
    #关闭数据库
    mydb.close()
