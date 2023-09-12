import tweepy
import configparser
import logging
import json
from datetime import datetime, timedelta
import config
import random

logger = logging.getLogger()

# Initialize Tweepy
def init_tweepy_api():
    config = configparser.ConfigParser()
    config.read('config.ini')
    auth = tweepy.OAuthHandler(config['Twitter']['CONSUMER_KEY'], config['Twitter']['CONSUMER_SECRET'])
    auth.set_access_token(config['Twitter']['ACCESS_TOKEN'], config['Twitter']['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# Tweet
def post_tweet(content):
    api = init_tweepy_api()
    api.update_status(status=content)
    logger.info("Posted a tweet.")

# Reply
def post_reply(user_screen_name, tweet_id, content):
    api = init_tweepy_api()
    api.update_status(status=f"@{user_screen_name} {content}", in_reply_to_status_id=tweet_id)
    logger.info(f"Posted a reply to {user_screen_name}.")

# Follow a user based on search query
def perform_follow():
    api = init_tweepy_api()
    search_query = random.choice(config['Twitter']['QUERY'].split(','))  # Assuming QUERY is comma-separated
    max_tweets = int(config['Twitter']['MAX_TWEETS'])
    
    for tweet in search_tweets(search_query, max_tweets):
        user = tweet.user
        account_age = (datetime.now() - user.created_at).days
        if user.followers_count > 100 and account_age > 120:
            api.create_friendship(user.id)
            logger.info(f"Followed {user.screen_name}")
            break  # Stop after one successful follow

# Unfollow users who are not in the target list and are not following back
def perform_unfollow():
    api = init_tweepy_api()
    with open('config/target_list.json', 'r') as f:
        target_list = json.load(f)
    
    for friend in tweepy.Cursor(api.friends).items():
        if friend.screen_name not in target_list and not friend.following:
            api.destroy_friendship(friend.id)
            logger.info(f"Unfollowed {friend.screen_name}")
            break  # Stop after one successful unfollow

# Retweet trending tweets based on topics
def perform_retweet():
    api = init_tweepy_api()
    topics = random.choice(config['Twitter']['TOPICS'].split(','))  # Assuming TOPICS is comma-separated
    
    for tweet in search_tweets(topics, 10):  # Assuming we search the top 10 trending tweets
        if tweet.user.followers_count > 5000 and not tweet.retweeted and not tweet.favorited:
            tweet.favorite()
            tweet.retweet()
            logger.info(f"Liked and retweeted tweet from {tweet.user.screen_name}")
            break  # Stop after one successful retweet

# Analytics
def get_analytics():
    api = init_tweepy_api()
    user = api.me()
    analytics_data = {
        'Followers': user.followers_count,
        'Following': user.friends_count,
        'Tweets': user.statuses_count,
        'Likes': user.favourites_count,
        'Account Created At': user.created_at
    }
    return analytics_data

# Search for tweets
def search_tweets(search_query, max_tweets):
    api = init_tweepy_api()
    return tweepy.Cursor(api.search_tweets, search_query).items(max_tweets)
