import twint
import pandas as pd
import requests
import re
import argparse

def TweetImpact():
    return "yeet"

headers = {'Authorization': 'prj_live_sk_97e3dcf111b9c25af024c95bf1b695ed087dc411'}

def radar_geocoding(location):
    params = (
        ('query', location),
    )
    try:
        response = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers, params=params)
        #print (response.json())
        country=response.json()['addresses'][0]['country']
        if country=='United States':

            return {'lat':response.json()['addresses'][0]['latitude'], 'lng': response.json()['addresses'][0]['longitude'], 'city': response.json()['addresses'][0]['city'], 'state':response.json()['addresses'][0]['state']}
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
    #print(loc)
    if loc == -1 or loc == None:
        return { 'lat': 'NA', 'lng': 'NA', 'city': 'NA', 'state': 'NA' }
    else:
        return loc

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
    c.Limit = 2
    c.Username = username
    c.Pandas = True

    twint.run.Followers(c)
    Followers_df = twint.storage.panda.Follow_df
    list_of_followers = Followers_df['followers'][username]
    return list_of_followers

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


### THIS IS WHERE THE MAIN IS ###

tweets_list = get_tweets_list("realDonaldTrump")
#followers_list = get_followers("realDonaldTrump")

favorites_locations = []
retweets_locations = []

j = 0
for tweet in tweets_list:
    favorites_list = get_favorited_list("realDonaldTrump", tweet) #names
    retweets_list = get_retweeters_list("realDonaldTrump", tweet) #names

    for fav in favorites_list:
        favorites_locations.append(get_user_location(fav, j))
        print(favorites_locations)
        j += 1
    for rtwt in retweets_list:
        retweets_locations.append(get_user_location(rtwt, j))
        j += 1

rows_list = []
# add the favorited locations
for i in favorites_locations:
    row_dict = {}
    row_dict['Type'] = 'Like'
    row_dict['lat'] = i['lat']
    row_dict['lng'] = i['lng']
    row_dict['city'] = i['city']
    row_dict['state'] = i['state']
    row_dict['Sentiment'] = '1'
    rows_list.append(row_dict)

# add the retweeted locations
for i in retweets_locations:
    row_dict = {}
    row_dict['Type'] = 'Retweet'
    row_dict['lat'] = i['lat']
    row_dict['lng'] = i['lng']
    row_dict['city'] = i['city']
    row_dict['state'] = i['state']
    row_dict['Sentiment'] = 'NA'
    rows_list.append(row_dict)

#create the dataframe
df = pd.DataFrame(rows_list)
print(df)
df.to_csv('./lordHelpUs.csv', index=False)