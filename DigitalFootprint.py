import twint
import pandas as pd
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

def get_followers(username):
    c = twint.Config()
    c.Limit = 10
    c.Username = username
    c.Pandas = True

    twint.run.Followers(c)
    Followers_df = twint.storage.panda.Follow_df
    list_of_followers = Followers_df['followers'][username]
    return list_of_followers

def get_tweets_list(username):
    c = twint.Config()
    c.Username = username
    c.Limit = 10
    c.Pandas = True
    c.Format = "ID {id}"
    twint.run.Search(c)

    tweets_df = twint.storage.panda.Tweets_df
    
    n_tweet = []
    for index, row in tweets_df.iterrows():
        n_tweet.append(row['id'])
    
    return n_tweet # return list of tweet ids


tweets_list = get_tweets_list("realDonaldTrump")
followers_list = get_followers("realDonaldTrump")

favorites_locations = []
retweets_locations = []

for tweet in tweets_list:
    favorites_list = get_favorited_list("realDonaldTrump", tweet) #names
    retweets_list = get_retweeters_list("realDonaldTrump", tweet) #names

    for fav in favorites_list:
        favorites_locations.append(get_user_location(fav))
    for rtwt in retweets_list:
        retweets_locations.append(et_user_location(rtwt))

rows_list = []
# add the favorited locations
for i in favorites_locations:
    row_dict = {}
    row_dict['Type'] = 'Like'
    row_dict['Location'] = i
    row_dict['Sentiment'] = 'POS'
    rows_list.append(row_dict)

# add the retweeted locations
for i in retweets_locations:
    row_dict = {}
    row_dict['Type'] = 'Retweet'
    row_dict['Location'] = i
    row_dict['Sentiment'] = 'NA'
    rows_list.append(row_dict)

#create the dataframe
df = pd.DataFrame(rows_list)
print(df)