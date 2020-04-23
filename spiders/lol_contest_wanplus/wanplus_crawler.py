import datetime
import json
import os
import time

import requests
from bs4 import BeautifulSoup

from utils import tool


class WanPlusLolDataSpider:
    def __init__(self, saving_path):
        # 抓取起止时间计算
        self._start_date = datetime.datetime.today() + datetime.timedelta(days=-365)  # 抓取开始日期
        self._end_date = (datetime.datetime.today() + datetime.timedelta(days=-1)).strftime("%Y%m%d")  # 抓取结束日期

        # 数据存储路径
        self._path_saving = saving_path  # 存储文件根目录
        self._path_date = os.path.join(saving_path, "date_list.json")  # 日期列表
        self._path_race = os.path.join(saving_path, "race_list.json")  # 比赛列表
        self._path_match = os.path.join(saving_path, "match")  # 场次信息表

        # 数据存储变量
        self.data_date = {}
        self.data_race = {}
        self.data_list_match = []

        # 请求信息
        self._date_list_url = "https://www.wanplus.com/ajax/schedule/list"  # 列表请求的url
        self._date_list_headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-length": "43",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "cookie": "UM_distinctid=16fd7fecc8499a-0b235e23a42caa-6701b35-1fa400-16fd7fecc856f0; wp_pvid=5198158261; gameType=2; wanplus_token=4cad6a33964b6e7332bbbecf75de892e; wanplus_storage=lf4m67eka3o; wanplus_sid=0d3b16b188a4c93171bc0d023a461bb3; wanplus_csrf=_csrf_tk_278248459; wp_info=ssid=s1273702015; Hm_lvt_f69cb5ec253c6012b2aa449fb925c1c2=1583294862,1585185668,1585185712; Hm_lpvt_f69cb5ec253c6012b2aa449fb925c1c2=1585208145; CNZZDATA1275078652=1738928189-1579872727-null%7C1585208374",
            "origin": "https://www.wanplus.com",
            "pragma": "no-cache",
            "referer": "https://www.wanplus.com/lol/schedule",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "x-csrf-token": "345357323",
            "x-requested-with": "XMLHttpRequest"
        }  # 列表请求的headers
        self._date_list_data = {
            "_gtk": "345357323",
            "game": "2",
            "time": "1571500800",
            "eids": "",
        }  # 列表请求的表单数据
        self._race_list_url = "https://www.wanplus.com/schedule/%s.html"  # 比赛请求的url
        self._race_list_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            # "cookie": "_uab_collina=157987680590179694225715; UM_distinctid=16fd7fecc8499a-0b235e23a42caa-6701b35-1fa400-16fd7fecc856f0; wp_pvid=5198158261; wanplus_token=4cad6a33964b6e7332bbbecf75de892e; wanplus_storage=lf4m67eka3o; wanplus_sid=0d3b16b188a4c93171bc0d023a461bb3; gameType=2; wanplus_csrf=_csrf_tk_278248459; wp_info=ssid=s8280898516; Hm_lvt_f69cb5ec253c6012b2aa449fb925c1c2=1585185668,1585185712,1585278669,1585474186; CNZZDATA1275078652=1738928189-1579872727-null%7C1585477331; Hm_lpvt_f69cb5ec253c6012b2aa449fb925c1c2=1585478088",
            "pragma": "no-cache",
            "referer": "https://www.wanplus.com/lol/schedule",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }  # 比赛请求的headers
        self._match_list_url = "https://www.wanplus.com/ajax/matchdetail/%s?_gtk=345357323"  # 场次请求的url
        self._match_list_referer = "https://www.wanplus.com/schedule/%s.html"  # 场次请求的headers中referer参数的值
        self._match_list_headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            # "cookie": "UM_distinctid=16fd7fecc8499a-0b235e23a42caa-6701b35-1fa400-16fd7fecc856f0; wp_pvid=5198158261; wanplus_token=4cad6a33964b6e7332bbbecf75de892e; wanplus_storage=lf4m67eka3o; wanplus_sid=0d3b16b188a4c93171bc0d023a461bb3; wanplus_csrf=_csrf_tk_278248459; gameType=2; wp_info=ssid=s1462349516; Hm_lvt_f69cb5ec253c6012b2aa449fb925c1c2=1585185712,1585278669,1585474186,1585693166; CNZZDATA1275078652=1738928189-1579872727-null%7C1585692760; Hm_lpvt_f69cb5ec253c6012b2aa449fb925c1c2=1585695009",
            "pragma": "no-cache",
            "referer": "",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "x-csrf-token": "345357323",
            "x-requested-with": "XMLHttpRequest"
        }  # 场次请求的headers

        # 载入已经抓取的数据
        self.load()

    def load(self):
        """载入已经抓取的数据"""
        if os.path.exists(self._path_date):
            self.data_date = tool.load_file_as_json(self._path_date)  # 载入日期比赛表

        if os.path.exists(self._path_race):
            self.data_race = tool.load_file_as_json(self._path_race)  # 载入日期比赛表

        self.data_list_match = os.listdir(self._path_match)  # 载入游戏信息文件列表

    def run_date_list(self):
        print("开始运行:日期列表爬虫......")
        # 统计需要抓取的日期列表
        all_date_list = list()  # 需要获取的日期列表
        curr_date = datetime.datetime.now() + datetime.timedelta(days=-1)
        while curr_date >= self._start_date:
            if (curr_date_str := curr_date.strftime("%Y%m%d")) not in self.data_date:
                all_date_list.append(curr_date_str)
            curr_date += datetime.timedelta(days=-1)
        print("需要抓取的日期总数:", len(all_date_list))

        if len(all_date_list) == 0:  # 若没有需要抓取的日期则结束运行
            return

        # 统计需要追溯的日期所在的周的时间戳
        need_date_list = list()  # 需要抓取的时间戳列表(所有的周日+最早的一天)
        for curr_date_str in all_date_list:
            curr_date = datetime.datetime.strptime(curr_date_str, "%Y%m%d")
            if curr_date.weekday() == 0:  # 若时间戳为周日
                need_date_list.append(curr_date_str)
        need_date_list.append(all_date_list[-1])  # 添加最早的一天
        print("需要抓取的时间戳总数:", len(need_date_list))

        # 依据时间戳抓取比赛数据
        for i in range(len(need_date_list)):
            curr_date_str = need_date_list[i]
            print("正在抓取时间戳:", i + 1, "/", len(need_date_list), "(", curr_date_str, ")")
            self._date_list_data["time"] = curr_date_str  # 列表请求的表单数据
            response = requests.post(self._date_list_url, headers=self._date_list_headers, data=self._date_list_data)
            if response.status_code == 200:
                response_json = json.loads(response.content.decode())
                for curr_date_str, date_infor in response_json["data"]["scheduleList"].items():
                    if curr_date_str not in self.data_date and int(curr_date_str) <= int(self._end_date):
                        self.data_date[curr_date_str] = list()
                        if date_infor["list"]:
                            for match in date_infor["list"]:
                                self.data_date[curr_date_str].append({
                                    "race_id": match["scheduleid"],
                                    "team_a_name": match["oneseedname"],
                                    "team_b_name": match["twoseedname"],
                                    "start_time": match["starttime"],
                                    "team_a_score": match["onewin"],
                                    "team_b_score": match["twowin"],
                                    "contest_name": match["ename"],
                                    "match_name": match["groupname"],
                                    "team_a_score_per": match["oneScore"],
                                    "team_b_score_per": match["twoScore"],
                                })
                tool.write_json_to_file(self._path_date, self.data_date)  # 存储日期比赛表
            time.sleep(tool.get_scope_random(5))

    def run_race_list(self):
        print("开始运行:场次列表爬虫......")
        # 统计需要抓取的比赛ID列表
        need_race_id_list = list()
        for date_name, date_race_list in self.data_date.items():
            for race_item in date_race_list:
                if race_item["race_id"] not in self.data_race:
                    need_race_id_list.append(race_item["race_id"])
        print("需要抓取的比赛数量:", len(need_race_id_list))

        # 抓取需要的比赛数据
        for i in range(len(need_race_id_list)):
            need_race_id = str(need_race_id_list[i])
            print("正在抓取比赛:", i + 1, "/", len(need_race_id_list), "(", need_race_id, ")")
            match_id_list = list()  # 场次ID列表
            response = requests.get(self._race_list_url % need_race_id, headers=self._race_list_headers)
            bs = BeautifulSoup(response.content.decode(), 'lxml')
            game_labels = bs.select("body > div > div.content > div.left > div:nth-child(1) > div > a")
            for game_label in game_labels:
                if game_label.has_attr("data-matchid"):
                    match_id_list.append(game_label["data-matchid"])
            self.data_race[need_race_id] = match_id_list
            tool.write_json_to_file(self._path_race, self.data_race)  # 存储日期比赛表
            time.sleep(tool.get_scope_random(5))

    def run_match_list(self):
        print("开始运行:场次信息爬虫......")
        # 统计需要抓取的场次ID列表
        need_match_id_list = dict()
        for race_id, match_id_list in self.data_race.items():
            for match_id in match_id_list:
                match_file_name = str(match_id) + ".json"
                if match_file_name not in self.data_list_match:
                    need_match_id_list[match_id] = race_id
        print("需要抓取的场次数量:", len(need_match_id_list))

        num = 1
        for match_id, race_id in need_match_id_list.items():
            print("正在抓取场次:", num, "/", len(need_match_id_list), "(", match_id, "-", race_id, ")")
            num += 1
            # 执行场次请求
            actual_url = self._match_list_url % match_id
            self._match_list_headers["referer"] = self._match_list_referer % race_id
            response = requests.get(actual_url, headers=self._match_list_headers)
            response_json = json.loads(response.content.decode())
            tool.write_json_to_file(os.path.join(self._path_match, str(match_id) + ".json"), response_json)  # 存储日期比赛表
            time.sleep(tool.get_scope_random(5))


if __name__ == "__main__":
    DATA_SAVING_PATH = "E:\\【微云工作台】\\数据\\英雄联盟比赛数据"
    spider = WanPlusLolDataSpider(saving_path=DATA_SAVING_PATH)
    spider.run_date_list()
    spider.run_race_list()
    spider.run_match_list()
