import twint
import pandas as pd
import requests
import re
import argparse
import boto3

def TweetImpact():
    return "yeet"

headers = {'Authorization': 'prj_live_sk_c0114cce2321a6741a5c129ea26cbf4a18196c2c'}

def radar_geocoding(location):
    params = (
        ('query', location),
    )
    try:
        response = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers, params=params)
        print (response.json())
        country=response.json()['addresses'][0]['country']
        if country=='United States':
            return {'lat':response.json()['addresses'][0]['latitude'], 'lng': response.json()['addresses'][0]['longitude'], 'state':response.json()['addresses'][0]['state']}
    except:
        return -1 #Fail Condition

def get_retweeters_list(username, tweet_id):
    r = requests.get('https://twitter.com/i/activity/retweeted_popup?id='+tweet_id)
    text = r.text
    x = re.findall('div class=\\\\"account  js-actionable-user js-profile-popup-actionable \\\\" data-screen-name=\\\\"(.+?)\\\\" data-user-id=\\\\"', text)
    return x[:1]

def get_favorited_list(username, tweet_id):
    r = requests.get('https://twitter.com/i/activity/favorited_popup?id='+tweet_id)
    text = r.text
    x = re.findall('div class=\\\\"account  js-actionable-user js-profile-popup-actionable \\\\" data-screen-name=\\\\"(.+?)\\\\" data-user-id=\\\\"', text)
    return x[:1]

def get_user_location(username, index):
    c = twint.Config()
    c.Username = username
    c.Format = "Location: {location}"
    c.Store_object = True
    c.User_full = True
    twint.run.Lookup(c)

    user = twint.output.users_list
    loc = radar_geocoding(user[index].location)
    print(loc)
    if loc == -1 or loc == None:
        return None
    else:
        return loc

def get_comments_list(username): #, tweet_id):
    c = twint.Config()
    c.To = "realDonaldTrump"
    c.Limit = 10
    c.Pandas = True
    c.Store_object = True
    twint.run.Search(c)

    tweets_list = twint.output.tweets_list
    comments = []
    for t in tweets_list:
        comments.append({'text': t.tweet, 'username': t.username})
    return comments

def get_followers(username):
    c = twint.Config()
    c.Limit = 10
    c.Username = username
    c.Store_object = True
    c.User_full = True

    twint.run.Followers(c)
    followers = twint.output.users_list

    usernames = []
    for f in followers:
        usernames.append(f.username)
    
    return usernames

def get_tweets_list(username):
    c = twint.Config()
    c.Username = username
    c.Limit = 2
    c.Pandas = True
    c.Format = "ID {id}"
    twint.run.Search(c)

    tweets_df = twint.storage.panda.Tweets_df
    
    n_tweet = []
    for index, row in tweets_df.iterrows():
        n_tweet.append(row['id'])
    
    return n_tweet # return list of tweet ids

def awsComprehend(text):
    comprehend = boto3.client('comprehend')
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    positive, negative, neutral, mixed = response['SentimentScore']['Positive'], response['SentimentScore']['Negative'], response['SentimentScore']['Neutral'], response['SentimentScore']['Mixed']
    list = [positive, negative, neutral, mixed]
    alist = [1, -1, 0, 0]

    max = list[0]
    num = 0
    for i in range(len(list)):
        if list[i] >= max:
            max = list[i]
            num = i
    

    return alist[num]


### THIS IS WHERE THE MAIN IS ###

tweets_list = get_tweets_list("realDonaldTrump")
followers_list = get_followers("realDonaldTrump")
comments_list = get_comments_list("realDonaldTrump")

favorites_locations = []
retweets_locations = []
followers_locations = []
comments_locations = []

j = 0
for tweet in tweets_list:
    favorites_list = get_favorited_list("realDonaldTrump", tweet) #names
    retweets_list = get_retweeters_list("realDonaldTrump", tweet) #names

    for fav in favorites_list:
        loc = get_user_location(fav, j)
        if loc:
            favorites_locations.append(loc)
        j += 1
    for rtwt in retweets_list:
        loc = get_user_location(rtwt, j)
        if loc:
            retweets_locations.append(loc)
        j += 1

for flw in followers_list:
    loc = get_user_location(flw, j)
    if loc:
        followers_locations.append(loc)
    j += 1

for com in comments_list:
    loc = get_user_location(com['username'], j)
    if loc:
        comments_locations.append({'text': com['text'], 'location': loc})
    j += 1

rows_list = []
# add the favorited locations
for i in favorites_locations:
    try:
        row_dict = {}
        row_dict['Type'] = 'Like'
        row_dict['lat'] = i['lat']
        row_dict['lng'] = i['lng']
        row_dict['state'] = i['state']
        row_dict['Sentiment'] = 1
        rows_list.append(row_dict)
    except:
        print(i)
        continue

# add the retweeted locations
for i in retweets_locations:
    try:
        row_dict = {}
        row_dict['Type'] = 'Retweet'
        row_dict['lat'] = i['lat']
        row_dict['lng'] = i['lng']
        row_dict['state'] = i['state']
        row_dict['Sentiment'] = 0
        rows_list.append(row_dict)
    except:
        print(i)
        continue

# add the followers locations
for i in followers_locations:
    try:
        row_dict = {}
        row_dict['Type'] = 'Follower'
        row_dict['lat'] = i['lat']
        row_dict['lng'] = i['lng']
        row_dict['state'] = i['state']
        row_dict['Sentiment'] = 0
        rows_list.append(row_dict)
    except:
        print(i)
        continue

# add the comments locations
for i in comments_locations:
    try:
        row_dict = {}
        row_dict['Type'] = 'Commenter'
        row_dict['lat'] = i['location']['lat']
        row_dict['lng'] = i['location']['lng']
        row_dict['state'] = i['location']['state']
        row_dict['Sentiment'] = awsComprehend(i['text'])
        rows_list.append(row_dict)
    except:
        print(i)
        continue

#create the dataframe
df = pd.DataFrame(rows_list)
print(df)
df.to_csv('./anAttemptWasMade.csv', index=False)