import json
import os
import random
from json import JSONDecodeError


def get_scope_random(num, scope=0.2):
    """生成散布于期望值附近一定范围内的随机数
    :param num: <float/int> 期望值
    :param scope: <float> 随机范围: 取值范围为[0,1],默认值为0.1(若不再取值范围内则使用默认值)
    """
    if not 0 <= scope <= 1:
        scope = 0.2
    return random.uniform((1 - scope) * float(num), (1 + scope) * float(num))


def load_file_as_string(path, encoding="UTF-8", ignore_blank_line=True):
    """读取文件内容为字符串
    :param path: <str> 文件路径
    :param encoding: <str> 编码格式
    :param ignore_blank_line: <bool> 是否跳过空行
    """
    if os.path.exists(path):
        try:
            result = ""
            with open(path, encoding=encoding) as fr:
                for line in fr:
                    if line != "" or not ignore_blank_line:
                        result += line
                fr.close()
            return result
        except FileNotFoundError:
            print("未找到文件:", path)


def load_file_as_json(path, encoding="UTF-8"):
    """读取文件内容为Json格式
    :param path: <str> 文件路径
    :param encoding: <str> 编码格式
    """
    if os.path.exists(path):
        try:
            with open(path, encoding=encoding) as fr:
                return json.loads(fr.read())
        except FileNotFoundError:
            print("未找到文件:", path)
            return dict()
        except JSONDecodeError:
            print("目标文件不是Json文件:" + path)
            return dict()


def write_string_to_file(path, data, encoding="UTF-8", type="w"):
    """将字符串写入到文件中
    :param path: <str> 文件路径
    :param data: <str> 需要写入的字符串
    :param encoding: <str> 编码格式
    """
    try:
        with open(path, type, encoding=encoding) as fr:
            fr.write(data)
    except FileExistsError:
        print("文件存在,写入失败:", path, "(type=", type, ")")


def write_json_to_file(path, data, ensure_ascii=False):
    """将Json格式数据写入到文件中
    :param path: <str> 文件路径
    :param data: 需要写入的Json格式数据
    :param ensure_ascii: <bool> 是否不允许包含非ASCII编码字符
    """
    write_string_to_file(path, json.dumps(data, ensure_ascii=ensure_ascii))
