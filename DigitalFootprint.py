import twint
import pandas
import requests
import re

def TweetImpact():
    return "yeet"

c = twint.Config()
c.Username = "realDonaldTrump"
#twint.run.Search(c)

def get_retweeters_list(username, tweet_id):
    r = requests.get('https://twitter.com/i/activity/retweeted_popup?id='+tweet_id)
    text = r.text
    x = re.findall('div class=\\\\"account ')