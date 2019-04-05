# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
# 对加载后的数据进行修改
import os
import sys
import argparse
from op_mysql import Mysql, get_db_conf

def upd_RY_ZHCH (mydb, yyyymm):
    rows=mydb.execute_sql('delete from RY_ZHCH where 月份=%s', (yyyymm))
    print('[%s][rowcount=%d]' %('delete', rows))
    rows=mydb.execute_sql('INSERT INTO RY_ZHCH ( 项目编号, 月份, 人月数 ) \
        (SELECT RY_YCOMS.项目编号, %s AS 月份, Sum(RY_YCOMS.人月) AS 人月 \
        FROM RY_YCOMS \
        WHERE (((RY_YCOMS.月份)<=%s)) \
        GROUP BY RY_YCOMS.项目编号)', (yyyymm, yyyymm))
    print('[%s][rowcount=%d]' %('计算项目累计人月insert', rows))
    return rows

def upd_project (mydb, yyyymm=None):
    xm_rows=mydb.execute_sql("UPDATE 项目损益明细 sy SET sy.所属部门级三 = sy.所属部门级二 \
        WHERE (sy.所属部门级三 = '' or sy.所属部门级三 is NULL) and	sy.所属部门级二<>''")

    xm_rows+=mydb.execute_sql("UPDATE 项目损益明细 sy SET sy.所属部门级三=sy.所属部门级一, sy.所属部门级二 = sy.所属部门级一 \
        WHERE (sy.所属部门级三 = '' or sy.所属部门级三 is NULL) and (sy.所属部门级二='' or sy.所属部门级二 is NULL) and sy.所属部门级一<>''")

    fxm_rows=mydb.execute_sql("UPDATE 非项目损益明细 nsy SET nsy.所属部门级三 = nsy.所属部门级二 \
    WHERE (nsy.所属部门级三 = '' or nsy.所属部门级三 is NULL) and nsy.所属部门级二<>''")

    fxm_rows+=mydb.execute_sql("UPDATE 非项目损益明细 nsy SET nsy.所属部门级三=nsy.所属部门级一, nsy.所属部门级二 = nsy.所属部门级一 \
        WHERE (nsy.所属部门级三 = '' or nsy.所属部门级三 is NULL) and (nsy.所属部门级二='' or nsy.所属部门级二 is NULL) and nsy.所属部门级一<>''")

    print('[%s][项目损益明细=%d] [非项目损益明细表=%d]' %('修改部门级三', xm_rows, fxm_rows))
    return xm_rows+fxm_rows

def upd_RY_YCOMS (mydb, yyyymm=None):
    rows=mydb.execute_sql("UPDATE RY_YCOMS ry SET ry.项目所属部门级三 = ry.项目所属部门级二 \
        WHERE (ry.项目所属部门级三 = '' or ry.项目所属部门级三 is NULL) and ry.项目所属部门级二<>''")

    rows+=mydb.execute_sql("UPDATE RY_YCOMS ry SET ry.项目所属部门级三=ry.项目所属部门级一, ry.项目所属部门级二 = ry.项目所属部门级一 \
        WHERE (ry.项目所属部门级三 = '' or ry.项目所属部门级三 is NULL) and (ry.项目所属部门级二='' or ry.项目所属部门级二 is null) and ry.项目所属部门级一<>''")

    rows+=mydb.execute_sql("UPDATE RY_YCOMS ry SET ry.员工所属部门级三 = ry.员工所属部门级二 \
        WHERE (ry.员工所属部门级三 = '' or ry.员工所属部门级三 is NULL) and ry.员工所属部门级二<>''")

    rows+=mydb.execute_sql("UPDATE RY_YCOMS ry SET ry.员工所属部门级三=ry.员工所属部门级一, ry.员工所属部门级二 = ry.员工所属部门级一 \
        WHERE (ry.员工所属部门级三 = '' or ry.员工所属部门级三 is NULL) and (ry.员工所属部门级二='' or ry.员工所属部门级二 IS NULL) and ry.员工所属部门级一<>''")

    rows+=mydb.execute_sql("UPDATE RY_YCOMS ry SET ry.项目所属部门级三=ry.员工所属部门级三, ry.项目所属部门级二=ry.员工所属部门级二, \
        ry.项目所属部门级一=ry.员工所属部门级一 \
        WHERE (ry.项目所属部门级三 = '' or ry.项目所属部门级三 is NULL) and (ry.项目所属部门级二='' or ry.项目所属部门级二 is null) and (ry.项目所属部门级一='' or ry.项目所属部门级一 is null)")

    print('[%s][RY_YCOMS=%d]' %('修改部门级三', rows))
    return rows

parser=argparse.ArgumentParser(description='同步数据到mysql后，进行相关数据调整')
parser.add_argument('--yyyymm', '-d', dest='yyyymm', type=str, required=False, help='input yyyymm[201812]')
parser.add_argument('--method', '-m', dest='method', required=True, help='选择调用方法', choices=['upd_RY_ZHCH', 'upd_RY_YCOMS', 'upd_project'])

if __name__ == "__main__":
    # 测试用
    args=list()
    if(len(sys.argv) == 1):
        parser.print_help()
        args.append(parser.parse_args('-m upd_RY_ZHCH -d 201812'.split()))
        args.append(parser.parse_args('-m upd_project'.split()))
        args.append(parser.parse_args('-m upd_RY_YCOMS'.split()))
    else:
        args.append(parser.parse_args())

    db_params=get_db_conf('database.ini')
    mydb = Mysql(**db_params)
    for arg in args:
        try:
            func=globals().get(arg.method)
            if(func!=None):
                func(mydb, yyyymm=arg.yyyymm)
            else:
                raise Exception("find function[{}] error".format(arg.method))  
            mydb.commit()
        except:
            mydb.rollback()

    #关闭数据库
    mydb.close()
