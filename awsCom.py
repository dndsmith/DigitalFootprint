import boto3

bucketName = 'cuhackit6'

def awsComprehend(text):
    comprehend = boto3.client('comprehend')
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    positive, negative, neutral, mixed = response['SentimentScore']['Positive'], response['SentimentScore']['Negative'], response['SentimentScore']['Neutral'], response['SentimentScore']['Mixed']
    list = [positive, negative, neutral, mixed]
    alist = ['positive', 'negative', 'neutral', 'mixed']

    max = list[0]
    num = 0
    for i in range(len(list)):
        if list[i] >= max:
            max = list[i]
            num = i

    return alist[num]

sentiment = []
s3 = boto3.resource('s3')
s3.meta.client.download_file(bucketName, 'data.txt', 'data.txt')
obj = s3.Object(bucketName, 'data.txt')
file = obj.get()['Body'].read().decode("utf-8")

file = file.splitlines()

for i in file:
    sentiment.append(awsComprehend(i))

newFile = 'sentiments.csv'

open(newFile, 'w').close()

for i in sentiment:
    with open(newFile, 'a') as f:
        f.write(i + ',')
        f.close()

s3 = boto3.client('s3')
s3.upload_file(newFile, bucketName, 'sentiments.csv')
