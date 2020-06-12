import datetime as dt

from twitterscraper import query_tweets

if __name__ == '__main__':
    # list_of_tweets = query_tweets("from:zaobaosg", 10)

    # print the retrieved tweets to the screen:
    for tweet in query_tweets("from:realDonaldTrump", begindate=dt.date(2020, 6, 2)):
        print(tweet)
