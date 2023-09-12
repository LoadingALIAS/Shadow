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

# Follow a user based on the timeline
def perform_follow():
    api = init_tweepy_api()
    timeline = api.home_timeline(count=50)

    # Load existing followed accounts
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

            # Update the list of followed accounts with the current timestamp
            followed_accounts[user.screen_name] = str(datetime.now())
            with open('followed_accounts.json', 'w') as f:
                json.dump(followed_accounts, f)

            break

# Unfollow users who are not in the target list and are not following back
def perform_unfollow():
    api = init_tweepy_api()

    # Load target list
    with open('config/target_list.json', 'r') as f:
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

def perform_retweet(is_blocked_keyword_present):
    api = init_tweepy_api()
    topics = random.choice(config['Twitter']['TOPICS'].split(','))  # Assuming TOPICS is comma-separated
    blocked_keywords = ['Ad', 'Promo', 'Advert', 'Advertisement', 'Promotion', 'Promotional', 'Newsletter']

    for tweet in search_tweets(topics, 10):  # Assuming we search the top 10 trending tweets
        tweet_text = tweet.text  # Assuming 'text' contains the text of the tweet you're retweeting
        user_screen_name = tweet.user.screen_name
        
        if tweet.user.followers_count > 2500 and not tweet.retweeted and not tweet.favorited:
            if not is_blocked_keyword_present(tweet_text, blocked_keywords) and not is_blocked_keyword_present(user_screen_name, blocked_keywords):
                tweet.favorite()
                tweet.retweet()
                logger.info(f"Liked and retweeted tweet from {tweet.user.screen_name}")
                break  # Stop after one successful retweet
            else:
                logger.info(f"Skipped retweet from {user_screen_name} due to keyword restrictions.")

# Search for tweets
def search_tweets(search_query, max_tweets):
    api = init_tweepy_api()
    return tweepy.Cursor(api.search_tweets, search_query).items(max_tweets)
