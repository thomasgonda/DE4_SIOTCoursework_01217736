# Adapted from GeeksforGeeksSentimentAnalysis

from forecastiopy import *
from datetime import datetime
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import csv
import time

while True:
    apikey = '84b416c5d6da987bf663ed1ced2da13e'
    London = [51.509865, -0.118092]

    fio = ForecastIO.ForecastIO(apikey,
                                units=ForecastIO.ForecastIO.UNITS_SI,
                                lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                                latitude=London[0], longitude=London[1])

    print('Latitude', fio.latitude, 'Longitude', fio.longitude)
    print('Timezone', fio.timezone, 'Offset', fio.offset)
    print(fio.get_url())  # You might want to see the request url

    csvtitle = 'Data_Weather_1.csv'
    loopweather = 0

    csvtitle = 'Data_Weather_1.csv'
    loopweather = 0
    start_time = time.time()
    upload_timer = time.time()
    print(start_time)

    if fio.has_currently() is True:
        currently = FIOCurrently.FIOCurrently(fio)
        print('Currently')

        with open(csvtitle, 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            temperature = currently.temperature
            apptemperature = currently.apparentTemperature
            humidity = currently.humidity
            cloudcover = currently.cloudCover
            uvindex = currently.uvIndex
            precipintensity = currently.precipIntensity
            visibility = currently.visibility
            ozone = currently.ozone
            pressure = currently.pressure
            windspeed = currently.windSpeed
            windgust = currently.windGust
            winddirection = currently.windBearing
            timestamp = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')

            rowweather = [loopweather, timestamp, temperature, apptemperature, humidity, cloudcover, visibility,
                          uvindex, precipintensity, ozone, pressure, windspeed, windgust, winddirection]

            writer.writerow(rowweather)
            csvfile.close()

            #time.sleep(180)
            loopweather = loopweather + 1
    else:
        print('No Currently data')

    class TwitterClient(object):
        '''
        Generic Twitter Class for sentiment analysis.
        '''

        def __init__(self):
            '''
            Class constructor or initialization method.
            '''
            # keys and tokens from the Twitter Dev Console
            consumer_key = 'gcMbYLC9TH64IN4xptAuDLTbC'
            consumer_secret = 'EKQ5oVjMFH9tnOKTVLSFCz3eVaNSYNDXpKY3c89Kcbc2P1RlWQ'
            access_token = '953234902027264001-7KqGaI9nnCojlmjdcW2h39UbBcSGAPx'
            access_token_secret = 'syFj4YT7f918j1I2ATgurtg9Idkjj8UuoBpbjvYH7SGvn'

            # attempt authentication
            try:
                # create OAuthHandler object
                self.auth = OAuthHandler(consumer_key, consumer_secret)
                # set access token and secret
                self.auth.set_access_token(access_token, access_token_secret)
                # create tweepy API object to fetch tweets
                self.api = tweepy.API(self.auth)
            except:
                print("Error: Authentication Failed")

        def clean_tweet(self, tweet):
            '''
            Utility function to clean tweet text by removing links, special characters
            using simple regex statements.
            '''
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

        def get_tweet_sentiment(self, tweet):
            '''
            Utility function to classify sentiment of passed tweet
            using textblob's sentiment method
            '''
            # create TextBlob object of passed tweet text
            analysis = TextBlob(self.clean_tweet(tweet))
            # set sentiment
            if analysis.sentiment.polarity > 0:
                return 'positive'
            elif analysis.sentiment.polarity == 0:
                return 'neutral'
            else:
                return 'negative'

        def get_tweets(self, query, geocode, since_id, count=10):
            '''
            Main function to fetch tweets and parse them.
            '''
            # empty list to store parsed tweets
            tweets = []

            try:
                # call twitter api to fetch tweets
                fetched_tweets = self.api.search(q=query, count=count)

                # parsing tweets one by one
                for tweet in fetched_tweets:
                    # empty dictionary to store required params of a tweet
                    parsed_tweet = {}

                    # saving text of tweet
                    parsed_tweet['text'] = tweet.text
                    # saving timestamp of tweet
                    parsed_tweet['timestamp'] = tweet.created_at
                    # saving id of tweet
                    parsed_tweet['id'] = tweet.id
                    # saving sentiment of tweet
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)

                        # return parsed tweets
                return tweets

            except tweepy.TweepError as e:
                # print error (if any)
                print("Error : " + str(e))


    def main():
        # creating object of TwitterClient Class
        api = TwitterClient()
        oldtweets = []
        start_time = time.time()
        upload_timer = time.time()
        print(start_time)
        last_id = 0
        loop = 0
        csvtitle = 'Data_Tweets_1.csv'
        title_iterator = 1

        # calling function to get most recent tweets
        tweetbatch = api.get_tweets(query='climate change', geocode=[-0.118092, 51.509865], since_id=last_id, count=100000)

        if tweetbatch is not None:  # check that there are new tweets
            freshtweets = [x for x in tweetbatch if x not in oldtweets]  # remove any that matched the last sample
            freshtweets.reverse()  # make chronological
            oldtweets = tweetbatch  # reassign the most recent batch of tweets

            # store sentiment, timestamp and text of each tweet in new line of csv
            with open(csvtitle, 'a', encoding='utf-8') as csvFile:
                writer = csv.writer(csvFile)

                # Calculate sentiment for each tweet
                for tweet in freshtweets:
                    sentiment = tweet['sentiment']
                    timestamp = tweet['timestamp']
                    text = tweet['text']
                    row = [loop, timestamp, sentiment, text]
                    writer.writerow(row)
                csvFile.close()

            # get last ID
            print(len(freshtweets))
            if len(freshtweets) > 0:
                last_id = freshtweets[-1]['id']

        # if 12 hours has passed upload the file and change title
        twelve_hours = 60 * 60 * 12
        upload_time_passed = time.time() - upload_timer
        if upload_time_passed > twelve_hours:
            upload_timer = time.time()  # reset to 0 seconds
            csvtitle = 'Data_Tweets_' + str(title_iterator) + '.csv'  # next title
            title_iterator = title_iterator + 1

        # wait 5 minutes and repeat
        time.sleep(180)
        loop = loop + 1

    if __name__ == "__main__":
        # calling main function
        main()
