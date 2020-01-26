import twint
import pandas as pd
import requests
import re
import argparse
import boto3
import googlemaps
import pprint

def google_geocoding(location, api_key):
    gmaps = googlemaps.Client(key=api_key)
    try:
        geocode_result = gmaps.geocode(location)
        print(geocode_result)
        return geocode_result[0]['geometry']['location']
    except:
        return -1#Fail

def TweetImpact():
    return "yeet"

def radar_geocoding(location, api_key):
    headers = {'Authorization': api_key}
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

def get_user_location(username, index, api_key):
    c = twint.Config()
    c.Username = username
    c.Format = "Location: {location}"
    c.Store_object = True
    c.User_full = True
    twint.run.Lookup(c)
    print(api_key)

    user = twint.output.users_list
    print(user[index].location)
    loc = google_geocoding(user[index].location, api_key)
    print(loc)
    if loc == -1 or loc == None:
        return None
    else:
        return loc

def get_comments_list(username): #, tweet_id):
    c = twint.Config()
    c.To = username
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
    c.Format = "Follower: {username} Tweet: {tweet}"

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

parser = argparse.ArgumentParser(description='Map digital footprint.')
parser.add_argument('--username', dest='username', type=str, default='realDonaldTrump',
                        help='enter name of Twitter user handle')
parser.add_argument('--google_key', dest='google_key', type=str,
                        help='enter google maps api key')
    
args = parser.parse_args()

tweets_list = get_tweets_list(args.username)
followers_list = get_followers(args.username)
comments_list = get_comments_list(args.username)

favorites_locations = []
retweets_locations = []
followers_locations = []
comments_locations = []

j = 0
for tweet in tweets_list:
    favorites_list = get_favorited_list(args.username, tweet) #names
    retweets_list = get_retweeters_list(args.username, tweet) #names

    for fav in favorites_list:
        loc = get_user_location(fav, j, args.google_key)
        print(loc)
        if loc:
            favorites_locations.append(loc)
        j += 1
    for rtwt in retweets_list:
        loc = get_user_location(rtwt, j, args.google_key)
        print(loc)
        if loc:
            retweets_locations.append(loc)
        j += 1

for flw in followers_list:
    loc = get_user_location(flw, j, args.google_key)
    print(loc)
    if loc:
        followers_locations.append(loc)
    j += 1

for com in comments_list:
    loc = get_user_location(com['username'], j, args.google_key)
    print(loc)
    if loc:
        comments_locations.append({'text': com['text'], 'location': loc})
    j += 1

print(favorites_locations)
print(retweets_locations)
rows_list = []
# add the favorited locations
for i in favorites_locations:
    try:
        row_dict = {}
        row_dict['Type'] = 'Like'
        row_dict['lat'] = i['lat']
        row_dict['lng'] = i['lng']
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
        row_dict['Sentiment'] = awsComprehend(i['text'])
        rows_list.append(row_dict)
    except:
        print(i)
        continue

#create the dataframe
print(rows_list)

df = pd.DataFrame(rows_list)
print(df)
df.to_csv('./noSleepItWouldSeem.csv', index=False)