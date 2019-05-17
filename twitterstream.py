# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 15:16:05 2019

@author: naman
"""
from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import tokens

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import re

#--------------------Twitter client------------

class TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuth().authenticate()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user
        
        
    def get_twitter_client_api(self):
        return self.twitter_client
    

    def get_user_tweets(self,num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id  =self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self,num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list 
    
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline = []
        for tweet in Cursor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline.append(tweet)
        return home_timeline
    
        

#---------------------twwitter authentication------
class TwitterAuth():
    def authenticate(self):
        auth = OAuthHandler(tokens.CONSUMER_KEY, tokens.CONSUMER_SECRET)
        auth.set_access_token(tokens.ACCESS_TOKEN, tokens.ACCESS_TOKEN_SECRET)
        return auth
        
        
#---------------------twitter streamer---------
#getting the stream of tweets
#create an object of StreamListener class that is used to stream out the data
class TwitterStream():
    
    def __init__(self):
        self.twitterAuth = TwitterAuth()
    
    def stream_tweets(self,fetched_tweet_filename, hash_tag_list):
        #handles authentication and tweet listener
        listener = TweetListener(fetched_tweet_filename)
        auth = self.twitterAuth.authenticate()
        stream = Stream(auth, listener)
        stream.filter(track = ["rahul gandhi", "narendra modi"])
        
        
    
        
#0-------------------stream Listener------------
#basic class for printing the data
class TweetListener(StreamListener):   #extends StreamListener class
    #override method from StreamListener class
    def __init__(self,fetched_tweet_filename):
        self.fetched_tweet_filename = fetched_tweet_filename
        
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweet_filename, 'a') as file:
                file.write(data)
            return True
        except BaseException as e:
            print("Error on data %s" %str(e))
        return True
    #override on_error method
    def on_error(self, status):
        if status == 420:
            #returning false in case rate limit is crossed
            return False
        print(status)

class TweetAnalyser():
    '''
    functionality for analysing and categorizong the content of the tweets
    '''
    def tweet_to_dataframe(self,tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['tweets'])
        #df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        #df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        #df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df

    def clean_tweets(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyse_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweets(tweet))

        if(analysis.sentiment.polarity > 0):
            return 1
        elif(analysis.sentiment.polarity ==0):
            return 0
        else:
            return -1
        
        
if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyser = TweetAnalyser()
    
    api = twitter_client.get_twitter_client_api()
    
    tweets = api.user_timeline(screen_name = "narendramodi", count = 300)
    
    df = tweet_analyser.tweet_to_dataframe(tweets)
    
    #tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweets']
    
    df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweets']])
    
    print(df.head(5))
    #-----------analysing the tweets------
    '''
    #get average length of the tweets from the dataframe
    print(np.mean(df['len']))
    #get the most liked tweets
    print(np.max(df['likes']))
    #most retweeted tweet
    print(np.max(df['retweets']))
    
    #Time-Series
    time_likes = pd.Series(data = df['likes'].values,index = df['date'] )
    time_likes.plot(figsize = (16,4), label ='likes', legend = True)
    time_likes = pd.Series(data = df['retweets'].values,index = df['date'] )
    time_likes.plot(figsize = (16,4), label ='retweets', legend = True, color = 'r')
    
    plt.show()'''
    
        
    
    
