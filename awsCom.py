import boto3

bucketName = 'cuhackit6'

#getting sentiment of each line
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
# read the contents of the file in the s3 bucket
file = obj.get()['Body'].read().decode("utf-8")

# split the lines so that each line can be fed line by line
file = file.splitlines()

# send each line to comprehend
for i in file:
    sentiment.append(awsComprehend(i))

newFile = 'sentiments.txt'

# append each line in the new file
for i in sentiment:
    with open(newFile, 'a') as f:
        f.write(i)

# has the problem of uploading the sentiments multiple times
# s3 = boto3.client('s3')
# s3.upload_file(newFile, bucketName, 'sentiments.txt')
