import twint
import pandas
import requests
import re
import argparse

def TweetImpact():
    return "yeet"

def get_retweeters_list(username, tweet_id):
    r = requests.get('https://twitter.com/i/activity/retweeted_popup?id='+tweet_id)
    text = r.text
    x = re.findall('div class=\\\\"account  js-actionable-user js-profile-popup-actionable \\\\" data-screen-name=\\\\"(.+?)\\\\" data-user-id=\\\\"', text)
    return x

def get_favorited_list(username, tweet_id):
    r = requests.get('https://twitter.com/i/activity/favorited_popup?id='+tweet_id)
    text = r.text
    x = re.findall('div class=\\\\"account  js-actionable-user js-profile-popup-actionable \\\\" data-screen-name=\\\\"(.+?)\\\\" data-user-id=\\\\"', text)
    return x

def get_user_location(username):
    c = twint.Config()
    c.Username = "realDonaldTrump"
    #c.Format = "Location: {location}"
    c.Pandas = True
    twint.run.Lookup(c)

    user_df = twint.storage.panda.User_df
    return user_df['location'] # return pandas df because why not

def get_comments_list(username): #, tweet_id):
    c = twint.Config()
    c.To = "realDonaldTrump"
    c.Limit = 1000
    c.Pandas = True
    twint.run.Search(c)

    replies_df = twint.storage.panda.Tweets_df
    return replies_df #[replies_df.conversation_id == tweet_id] # return pandas df

def get_tweets_list(username):
    c = twint.Config()
    c.Username = username
    c.Limit = 10
    c.Pandas = True
    c.Format = "ID {id}"
    twint.run.Search(c)

    tweets_df = twint.storage.panda.Tweets_df
    return tweets_df

#print(get_retweeters_list("realDonaldTrump", "1221140946320084995"))
get_tweets_list("realDonaldTrump")
for tweet in tweets_df:
    get_retweeters_list("RealDonaldTrump", tweet.id)
    
