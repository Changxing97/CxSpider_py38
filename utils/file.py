"""
工具类：文件读写
"""

import copy
import json
from json import JSONDecodeError


def as_string(path, encoding="UTF-8"):
    """ 加载文件内容为字符串格式
    :param path: <str> 要加载的文件的地址路径
    :param encoding: <str> 读取文件时使用的编码格式
    :return: <str> 读取完成的字符串格式数据
    """
    try:
        result = ""
        with open(path, encoding=encoding) as fr:
            for line in fr:
                if line is not None or line == "":
                    result += line
        return result
    except FileNotFoundError:
        print("[Warning] 未找到文件(" + path + ")")


def as_json(path, encoding="UTF-8"):
    """ 加载文件内容为Json格式
    :param path: <str> 要加载的Json文件的地址路径
    :param encoding: <str> 读取文件时使用的编码格式
    :return: <dict> 读取完成的Json格式数据
    """
    try:
        file = open(path, encoding=encoding)
        temp_json = copy.deepcopy(json.loads(file.read()))
        file.close()
        return temp_json
    except FileNotFoundError:
        print("[Warning] 未找到Json文件(" + path + ")")
    except JSONDecodeError:
        print("[Warning] 目标文件不是Json文件(" + path + ")")


def write_string(path, string, encoding="UTF-8", type="a+"):
    """ 写入String到文件中
    :param path: <str> 要写入的文件的地址路径
    :param string: <str> 要写入到文件的字符串
    :param encoding: <str> 写入文件的编码格式
    """
    try:
        with open(path, type, encoding=encoding) as fr:
            fr.write(string)
    except FileExistsError:
        print("[Warning] 文件已经存在，写入失败(" + path + ")")
