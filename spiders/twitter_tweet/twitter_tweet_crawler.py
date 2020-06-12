import time

from spiders.twitter_tweet import twitter_scraper

from utils import mysql
from utils import tool


def translate_to_list(tweet_list):
    """ 将结果转化为List格式

    :param tweet_list: 推文列表
    :return: <list> List格式推文列表
    """
    tweet_real_list = list()
    for tweet in tweet_list:
        tweet_real_list.append({
            "tweetId": tweet["tweetId"],
            "isRetweet": tweet["isRetweet"],
            "time": tweet["time"],
            "text": tweet["text"],
            "replies": tweet["replies"],
            "retweets": tweet["retweets"],
            "likes": tweet["likes"]
        })
    return tweet_real_list


def get_earliest_tweet_stamp(tweet_list):
    """ 获取推文列表最早的推文的时间戳

    :param tweet_list: 推文列表
    :return: <int> 最早的推文的时间戳
    """
    first_page_time = None
    for tweet in tweet_list:
        tweet_time_stamp = int(time.mktime(time.strptime(str(tweet["time"]), "%Y-%m-%d %H:%M:%S")))
        if first_page_time is None:
            first_page_time = tweet_time_stamp
        elif first_page_time > tweet_time_stamp:
            first_page_time = tweet_time_stamp
    return first_page_time


def crawler_item(user_name: str, media_id: int, media_name: str, mt, begin_time: str, end_time: str):
    """ 抓取单账号推文信息

    :param user_name: <str> 账号名称
    :param media_id: <int> 媒体ID
    :param media_name: <str> 媒体名称
    :param begin_time: <str> 抓取开始时间范围
    :param end_time: <str> 抓取结束时间范围
    :return: <None> 已将结果存入数据库
    """
    # 转换变量类型
    begin_time_stamp = int(time.mktime(time.strptime(begin_time, "%Y-%m-%d %H:%M:%S")))  # 抓取开始时间范围
    end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))  # 抓取结束时间范围

    # 抓取第1页(并判断是否包含所有要抓取的推文)
    # try:
    tweet_list = translate_to_list(twitter_scraper.get_tweets(user_name, pages=1))  # 抓取推文数据
    # except Exception as e:
    #     print(e)
    #     print("抓取页数:", 1, "(账号不存在)")
    #     return
    first_page_time = get_earliest_tweet_stamp(tweet_list)  # 获取推文列表最早的推文的时间戳

    # 若第1页不包含所有要抓取的推算，则计算并抓取所需的页数
    if first_page_time is None:
        print("抓取页数:", 1, "(账户没有发布过推文)")
    elif first_page_time > begin_time_stamp:
        page_num = 5 * (time.time() - begin_time_stamp) / (time.time() - first_page_time)
        tweet_list = translate_to_list(twitter_scraper.get_tweets(user_name, pages=int(page_num)))  # 抓取推文数据
        print("抓取页数:", int(page_num))
        first_page_time = get_earliest_tweet_stamp(tweet_list)  # 获取推文列表最早的推文的时间戳
        if first_page_time > begin_time_stamp:
            print("抓取页数不足!!!")
    else:
        print("抓取页数:", 1)
    print("抓取推文数:", len(tweet_list))

    # 整理推文列表
    writing_list = list()
    for tweet in tweet_list:
        tweet_time_stamp = int(time.mktime(time.strptime(str(tweet["time"]), "%Y-%m-%d %H:%M:%S")))
        if end_time_stamp >= tweet_time_stamp >= begin_time_stamp:  # 判断推文发表时间是否在时间范围内
            writing_list.append({
                "media_id": media_id,
                "media_name": media_name,
                "tweet_id": tweet["tweetId"],
                "is_retweet": tweet["isRetweet"],
                "time": tweet["time"],
                "text": tweet["text"],
                "replies": tweet["replies"],
                "retweets": tweet["retweets"],
                "likes": tweet["likes"]
            })

    write_num = mysql.insert_pure(mt, writing_list)  # 将数据写入到数据库
    print("存储推文数:", write_num)


if __name__ == "__main__":
    SETTING_PATH = "E:\\【微云工作台】\\数据\\华榜爬虫数据\\media_list_setting.json"
    settings = tool.load_file_as_json(SETTING_PATH)
    mt = mysql.MysqlTable(settings["tweet_mysql_table_infor"])  # 获取数据表信息

    for media in settings["media_list"]:
        # if int(media[0]) < 37:
        #     continue

        print("开始抓取媒体:", media[1], "(", media[0], ")", "-", media[3], "(", media[2], ")")
        crawler_item(user_name=media[2], media_id=media[0], media_name=media[1], mt=mt,
                     begin_time="2020-06-02 00:00:00", end_time="2020-06-02 23:59:59", )
        time.sleep(tool.get_scope_random(5))
