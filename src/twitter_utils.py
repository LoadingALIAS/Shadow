import tweepy
import configparser
import logging

logger = logging.getLogger()

# Initialize Tweepy API
def init_tweepy_api():
    config = configparser.ConfigParser()
    config.read('config.ini')
    auth = tweepy.OAuthHandler(config['Twitter']['CONSUMER_KEY'], config['Twitter']['CONSUMER_SECRET'])
    auth.set_access_token(config['Twitter']['ACCESS_TOKEN'], config['Twitter']['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# Post a tweet
def post_tweet(content):
    api = init_tweepy_api()
    api.update_status(status=content)
    logger.info("Posted a tweet.")

# Post a reply
def post_reply(user_screen_name, tweet_id, content):
    api = init_tweepy_api()
    api.update_status(status=f"@{user_screen_name} {content}", in_reply_to_status_id=tweet_id)
    logger.info(f"Posted a reply to {user_screen_name}.")

# Follow a user
def follow_user(user):
    api = init_tweepy_api()
    criteria = user.followers_count > 200 and user.statuses_count > 100
    if criteria:
        api.create_friendship(user.id)
        logger.info(f"Followed {user.screen_name}")

# Unfollow a user
def unfollow_user(user):
    api = init_tweepy_api()
    if not user.following:
        api.destroy_friendship(user.id)
        logger.info(f"Unfollowed {user.screen_name}")

# Like and retweet a tweet
def like_and_retweet(tweet):
    api = init_tweepy_api()
    if not tweet.retweeted and not tweet.favorited:
        tweet.favorite()
        tweet.retweet()
        logger.info(f"Liked and retweeted tweet from {tweet.user.screen_name}")

# Analytics
def get_analytics():
    api = init_tweepy_api()
    user = api.me()
    logger.info(f"Followers: {user.followers_count}, Following: {user.friends_count}")

# Search for tweets
def search_tweets(search_query, max_tweets):
    api = init_tweepy_api()
    return tweepy.Cursor(api.search_tweets, search_query).items(max_tweets)
