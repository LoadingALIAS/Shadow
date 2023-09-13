import tweepy
import configparser
import logging
import re
import random

import database_utils

from datetime import datetime, timedelta

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# Logging
logger = logging.getLogger()

# Define Blocked Keywords Filter
blocked_keywords = [keyword.strip() for keyword in config.get('Keywords', 'blocked_keywords').split(',')]

def is_blocked_keyword_present(text):
    for keyword in blocked_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.I):
            return True
    return False

# Tweet
def post_tweet(api, content):
    api.update_status(status=content)
    logger.info("Posted a tweet.")

# Reply
def post_reply(api, user_screen_name, tweet_id, content):
    api.update_status(status=f"@{user_screen_name} {content}", in_reply_to_status_id=tweet_id)
    logger.info(f"Posted a reply to {user_screen_name}.")

# Follow a User Based on Timeline
def perform_follow(api):
    timeline = api.home_timeline(count=50)

    for tweet in timeline:
        user = tweet.user
        account_age = (datetime.now() - user.created_at).days
        if user.followers_count > 100 and account_age > 120:
            api.create_friendship(user.id)
            logger.info(f"Followed {user.screen_name}")

            # Update 'followed accounts' w/ the Current Timestamp using SQLite
            database_utils.add_followed_account(user.screen_name)

            break

def perform_unfollow(api):
    # Load target list from SQLite DB
    target_list = database_utils.get_all_target_accounts()  # Changed Line

    # Get followed accounts from SQLite database
    followed_accounts = {account[0]: account[1] for account in database_utils.get_all_followed_accounts()}

    for friend in tweepy.Cursor(api.friends).items():
        if friend.screen_name not in target_list and not friend.following:
            follow_date_str = followed_accounts.get(friend.screen_name, '')
            if follow_date_str:
                follow_date = datetime.strptime(follow_date_str, '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.now() - follow_date).days >= 8:
                    api.destroy_friendship(friend.id)
                    logger.info(f"Unfollowed {friend.screen_name}")

                    # Remove from the list of followed accounts using SQLite
                    database_utils.remove_followed_account(friend.screen_name)

                    break  # Stop after one successful unfollow

# Retweet
def perform_retweet(api):
    # Read topics from config.ini
    topics = config.get('Topics', 'TOPICS').split(', ')
    random_topic = random.choice(topics)

    for tweet in search_tweets(api, 10):  # Assuming we search the top 10 trending tweets
        tweet_text = tweet.text
        user_screen_name = tweet.user.screen_name

        if tweet.user.followers_count > 2500 and not tweet.retweeted and not tweet.favorited:
            if not is_blocked_keyword_present(tweet_text) and not is_blocked_keyword_present(user_screen_name):
                tweet.favorite()
                tweet.retweet()
                logger.info(f"Liked and retweeted tweet from {tweet.user.screen_name}")
                break
            else:
                logger.info(f"Skipped retweet from {user_screen_name} due to keyword restrictions.")

# Search for Tweets
def search_tweets(api, max_tweets):
    
    # Read query terms from config.ini
    query_terms = config.get('Search', 'QUERY').split(', ')
    random_query = random.choice(query_terms)
    
    return tweepy.Cursor(api.search_tweets, random_query).items(max_tweets)