import tweepy
import configparser
import logging
import json
from datetime import datetime, timedelta
import random

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# Logging
logger = logging.getLogger()

# Initialize Tweepy
def init_tweepy_api():
    try:
        auth = tweepy.OAuthHandler(config['Twitter']['CONSUMER_KEY'], config['Twitter']['CONSUMER_SECRET'])
        auth.set_access_token(config['Twitter']['ACCESS_TOKEN'], config['Twitter']['ACCESS_TOKEN_SECRET'])
        api = tweepy.API(auth, wait_on_rate_limit=True)
        return api
    except Exception as e:
        logger.error(f"Failed to initialize Tweepy API: {e}")
        raise

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

# Follow a User Based on Timeline
def perform_follow():
    api = init_tweepy_api()
    timeline = api.home_timeline(count=50)

    # Load Existing 'followed accounts'
    try:
        with open('followed_accounts.json', 'r') as f:
            followed_accounts = json.load(f)
    except FileNotFoundError:
        followed_accounts = {}

    for tweet in timeline:
        user = tweet.user
        account_age = (datetime.now() - user.created_at).days
        if user.followers_count > 100 and account_age > 120:
            api.create_friendship(user.id)
            logger.info(f"Followed {user.screen_name}")

            # Update 'followed accounts' w/ the Current Timestamp
            followed_accounts[user.screen_name] = str(datetime.now())
            with open('followed_accounts.json', 'w') as f:
                json.dump(followed_accounts, f)

            break

# Unfollow - Not in Target List; Not Following Back Within 8 Days.
def perform_unfollow():
    api = init_tweepy_api()

    # Load target list
    with open('target_list.json', 'r') as f:
        target_list = json.load(f)

    # Load followed accounts
    try:
        with open('followed_accounts.json', 'r') as f:
            followed_accounts = json.load(f)
    except FileNotFoundError:
        followed_accounts = {}

    for friend in tweepy.Cursor(api.friends).items():
        if friend.screen_name not in target_list and not friend.following:
            follow_date_str = followed_accounts.get(friend.screen_name, '')
            if follow_date_str:
                follow_date = datetime.strptime(follow_date_str, '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.now() - follow_date).days >= 8:
                    api.destroy_friendship(friend.id)
                    logger.info(f"Unfollowed {friend.screen_name}")

                    # Remove from the list of followed accounts
                    del followed_accounts[friend.screen_name]
                    with open('followed_accounts.json', 'w') as f:
                        json.dump(followed_accounts, f)

                    break  # Stop after one successful unfollow

# Retweet
def perform_retweet(is_blocked_keyword_present):
    api = init_tweepy_api()
    
    # Read topics and blocked keywords from config.ini
    topics = config.get('Topics', 'TOPICS').split(', ')
    random_topic = random.choice(topics)
    blocked_keywords = config.get('Keywords', 'blocked_keywords').split(',')

    for tweet in search_tweets(random_topic, 10):  # Assuming we search the top 10 trending tweets
        tweet_text = tweet.text
        user_screen_name = tweet.user.screen_name

        if tweet.user.followers_count > 2500 and not tweet.retweeted and not tweet.favorited:
            if not is_blocked_keyword_present(tweet_text, blocked_keywords) and not is_blocked_keyword_present(user_screen_name, blocked_keywords):
                tweet.favorite()
                tweet.retweet()
                logger.info(f"Liked and retweeted tweet from {tweet.user.screen_name}")
                break
            else:
                logger.info(f"Skipped retweet from {user_screen_name} due to keyword restrictions.")

# Search for Tweets
def search_tweets(max_tweets):
    api = init_tweepy_api()
    
    # Read query terms from config.ini
    query_terms = config.get('Search', 'QUERY').split(', ')
    random_query = random.choice(query_terms)
    
    return tweepy.Cursor(api.search_tweets, random_query).items(max_tweets)