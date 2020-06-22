import os
from functions import clean_tweet
from functions import sentiment_analyzer_scores
import tweepy
from tweepy import OAuthHandler

class TwitterClient(object):
    def __init__(self):
        consumer_key = os.environ.get('consumer_key')
        consumer_secret = os.environ.get('consumer_secret')
        access_token = os.environ.get('access_token')
        access_token_secret = os.environ.get('access_token_secret')
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def simple_analysis(self, query):
        fetched_tweets = []
        try:
            for tweet in tweepy.Cursor(self.api.search, lang='en', count=100, q=query).items(100):
                fetched_tweets.append(tweet)
        except:
            pass

        tweets = []
        try:
            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['status'] = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                y = clean_tweet(tweet.text)
                parsed_tweet['text'] = y
                parsed_tweet['sentiment'] = sentiment_analyzer_scores(y)
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            return tweets
        except tweepy.TweepError as e:
            print("Error : " + str(e))