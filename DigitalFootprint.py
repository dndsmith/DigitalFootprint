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

#print(get_retweeters_list("realDonaldTrump", "1221140946320084995"))