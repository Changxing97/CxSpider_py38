# 玩加(wanplus)电竞英雄联盟比赛数据爬虫
爬虫主要包括三个部分，分别为：
* 抓取各个日期包含的比赛ID——日期列表爬虫
* 抓取比赛ID抓取比赛包含的游戏场次ID——场次列表爬虫
* 根据游戏场次ID抓取该场游戏的信息——场次信息爬虫

爬虫依赖的包：beautifulSoup4,lxml,requests
## 日期列表爬虫(date_list)
浏览器地址:https://www.wanplus.com/lol/schedule

Ajax地址:https://www.wanplus.com/ajax/schedule/list
## 场次列表爬虫(race_list)
浏览器地址:https://www.wanplus.com/schedule/58822.html
## 场次信息爬虫(match_list)
浏览器Ajax地址示例:https://www.wanplus.com/ajax/matchdetail/65029?_gtk=345357323


