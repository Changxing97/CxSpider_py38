import time

from twitter_scraper import Profile

from utils import mysql
from utils import tool


def crawler_item(browser, user_name: str, media_id: int, media_name: str, mt, xpath):
    """ 抓取单个账号用户信息

    :param user_name: <str> 账号名称
    :param media_id: <int> 媒体ID
    :param media_name: <str> 媒体名称
    :return: <None> 已将结果存入数据库
    """
    # 使用twitter-scraper包抓取账户信息(关注数+正在关注数可能错误)
    try:
        profile = Profile(user_name)
    except:
        print("账号不存在!")
        return
    writing_item = profile.to_dict()
    writing_item["media_id"] = media_id
    writing_item["media_name"] = media_name

    # 抓取账户粉丝数和正在关注数(Selenium爬虫)
    browser.get("https://twitter.com/" + user_name)
    time.sleep(tool.get_scope_random(12))
    following_count = None
    followers_count = None
    try:
        following_count = browser.find_element_by_xpath(xpath["following_count"][0]).get_attribute("title")
        followers_count = browser.find_element_by_xpath(xpath["followers_count"][0]).get_attribute("title")
    except:
        try:
            following_count = browser.find_element_by_xpath(xpath["following_count"][1]).get_attribute("title")
            followers_count = browser.find_element_by_xpath(xpath["followers_count"][1]).get_attribute("title")
        except:
            print("Selenium抓取关注数+正在关注失败!")

    # 依据Selenium爬虫结果修正抓取结果
    if following_count is not None:
        following_count = following_count.replace(",", "")
        print("修正正在关注数量:", writing_item["following_count"], "→", following_count)
        writing_item["following_count"] = following_count
    if followers_count is not None:
        followers_count = followers_count.replace(",", "")
        print("修正关注者数量:", writing_item["followers_count"], "→", followers_count)
        writing_item["followers_count"] = followers_count

    # 将数据写入到数据库
    writing_list = list()
    writing_list.append(writing_item)
    write_num = mysql.insert_pure(mt, writing_list)
    print("存储记录数:", write_num)
    print(writing_list)


if __name__ == "__main__":
    SETTING_PATH = "E:\\【微云工作台】\\数据\\华榜爬虫数据\\media_list_setting.json"
    settings = tool.load_file_as_json(SETTING_PATH)
    mt = mysql.MysqlTable(settings["user_mysql_table_infor"])  # 获取数据表信息

    browser = tool.open_chrome(use_user_dir=False)  # 通过Selenium打开Chrome浏览器

    for media_item in settings["media_list"]:
        print("开始抓取媒体:", media_item[1], "(", media_item[0], ")", "-", media_item[3], "(", media_item[2], ")")
        crawler_item(browser, media_item[2], media_item[0], media_item[1], mt, settings["user_xpath"])
        time.sleep(tool.get_scope_random(1))

    browser.close()
