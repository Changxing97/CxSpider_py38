# coding=utf-8

"""
爬虫工具-基础工具包：MySQL数据库支持函数
"""

import re

import mysql.connector


class MysqlTable:
    def __init__(self, infor):
        self.host = infor["host"]
        self.user = infor["user"]
        self.password = infor["pswd"]
        self.database = infor["database"]
        self.table = infor["table"]

        if "use_unicode" in infor:
            self.use_unicode = infor["use_unicode"]
        else:
            self.use_unicode = True


def select(mt: MysqlTable, columns: list, sql_where: str = ""):
    """ SELECT读取MySQL数据库的数据

    :param mt: <MysqlTable> MySQL数据表信息
    :param columns: <list:str> 需要读取的字段名称列表
    :param sql_where: <str> 在执行SELECT语句时是否添加WHERE子句(默认为空,如添加应以WHERE开头)
    :return: <list> 读取的数据结果
    """
    mysql_database = mysql.connector.connect(host=mt.host, user=mt.user, password=mt.password,
                                             database=mt.database, use_unicode=mt.use_unicode)
    mysql_cursor = mysql_database.cursor()  # 获取数据库操作句柄
    mysql_cursor.execute(sql_select(mt.table, columns, sql_where))  # 生成并执行SELECT语句
    mysql_results = mysql_cursor.fetchall()  # 获取SQL语句执行的返回多行记录的结果
    select_result = []
    for mysql_result in mysql_results:  # 遍历:SQL语句检索的各行记录
        if len(columns) > 1:  # 处理读取字段数超过1个的情况
            select_item = []
            for i in range(len(columns)):
                select_item.append(mysql_result[i])
            select_result.append(select_item)
        elif len(columns) == 1:  # 处理读取字段数为1个的情况
            select_result.append(mysql_result[0])
    mysql_database.shutdown()
    return select_result


def create(mt: MysqlTable, sql: str):
    """ 执行创建数据表的SQL语句

    :param mt: <MysqlTable> MySQL数据表信息
    :param sql: <str> 创建数据表的SQL语句
    """
    mysql_database = mysql.connector.connect(host=mt.host, user=mt.user, password=mt.password)
    mysql_cursor = mysql_database.cursor()
    mysql_cursor.execute(sql)


def insert(mt: MysqlTable, data: list):
    """ INSERT写入数据到MySQL数据库

    :param mt: <MysqlTable> MySQL数据表信息
    :param data: <list:list> 需要写入的多条记录(所有记录的字段名与第一条记录的字段名统一)
    :return: <bool> 写入数据是否成功
    """
    if len(data) == 0:  # 处理需要写入的记录数为0的情况
        return 0

    mysql_database = mysql.connector.connect(host=mt.host, user=mt.user, password=mt.password, database=mt.database,
                                             use_unicode=mt.use_unicode)
    mysql_cursor = mysql_database.cursor()
    sql, val = sql_insert(mt.table, data)
    mysql_cursor.executemany(sql, val)  # 执行SQL语句
    mysql_database.commit()  # 数据表内容更新提交语句
    return mysql_cursor.rowcount


def insert_pure(mt: MysqlTable, data: list):
    """ INSERT写入数据到MySQL数据库(使用纯粹SQL语句)

    :param mt: <MysqlTable> MySQL数据表信息
    :param data: <list:list> 需要写入的多条记录(所有记录的字段名与第一条记录的字段名统一)
    :return: <bool> 写入数据是否成功
    """
    if len(data) == 0:  # 处理需要写入的记录数为0的情况
        return 0

    mysql_database = mysql.connector.connect(host=mt.host, user=mt.user, password=mt.password, database=mt.database,
                                             use_unicode=mt.use_unicode)
    mysql_cursor = mysql_database.cursor()
    sql = sql_insert_pure(mt.table, data)
    mysql_cursor.execute(sql)  # 执行SQL语句
    mysql_database.commit()  # 数据表内容更新提交语句
    return mysql_cursor.rowcount


def sql_select(table: str, columns: list, where: str = ""):
    """ [生成SQL语句]SELECT语句
    :param table: <str> 需要SELECT的表单名称
    :param columns: <list:str> 需要读取的字段名称列表
    :param where: <str> 在SELECT时执行的WHERE子句(默认为空,如添加应以WHERE开头)
    :return: <str> 生成完成的SELECT(MySQL)语句
    """
    sql = "SELECT "
    for column in columns:
        sql += column + ","
    return re.sub(",$", " FROM " + table + " " + where, sql)


def sql_insert(table: str, datas: list):
    """ [生成SQL语句]INSERT语句
    :param table: <str> 需要写入的MySQL数据表名称
    :param datas: <list:list> 需要写入的多条记录(所有记录的字段名与第一条记录的字段名统一)
    :return: <str> SQL语句部分, <list> 写入数据部分 / <None> 需要写入的数据存在问题
    """
    if len(datas) == 0:
        return None

    # 生成SQL语句
    column_list = []
    column_part = ""  # SQL语句列名部分
    value_part = ""  # SQL语句数据部分
    for column in datas[0]:
        column_list.append([column, type(datas[0][column])])
        column_part += "`" + column + "`,"
        if isinstance(datas[0][column], str):
            value_part += "%s,"
        elif isinstance(datas[0][column], int) or isinstance(datas[0][column], float):
            value_part += "%d,"
        else:
            value_part += "%s,"
    column_part = re.sub(",$", "", column_part)
    value_part = re.sub(",$", "", value_part)
    sql = "INSERT INTO " + table + " (" + column_part + ") VALUES (" + value_part + ")"  # 拼接SQL语句

    # 生成写入数据
    val = []
    for data in datas:
        val_item = []
        for column in column_list:
            if column[0] in data and (column[1] == int or column[1] == float or column[1] == str):
                val_item.append(data[column[0]])
            else:
                if column[1] == int or column[1] == float:
                    val_item.append(0)
                else:
                    val_item.append("")
        val.append(val_item)
    return sql, val


def sql_insert_pure(table: str, datas: list):
    """ [生成SQL语句]INSERT语句(纯粹SQL语句,部分sql和val)
    :param table: <str> 需要写入的MySQL数据表名称
    :param datas: <list:list> 需要写入的多条记录(所有记录的字段名与第一条记录的字段名统一)
    :return: <str> SQL语句部分
    """
    if len(datas) == 0:
        return None

    # 生成SQL语句
    column_list = []
    column_part = ""  # SQL语句列名部分
    for column in datas[0]:
        column_list.append([column, type(datas[0][column])])
        column_part += "`" + column + "`,"
    column_part = re.sub(",$", "", column_part)

    # 生成写入数据
    value_list = []
    for data in datas:
        val_item = "("
        for column in column_list:
            if column[0] in data and data[column[0]] is not None:
                if column[1] == int or column[1] == float or column[1] == bool:
                    val_item += str(data[column[0]]) + ","
                else:
                    val_item += "'" + str(data[column[0]]).replace("'", "") + "',"
            else:
                if column[1] == int or column[1] == float:
                    val_item += "0,"
                else:
                    val_item += "'',"
        val_item = re.sub(",$", ")", val_item)
        value_list.append(val_item)

    return "INSERT INTO " + table + " (" + column_part + ") VALUES " + ",".join(value_list)  # 拼接SQL语句
