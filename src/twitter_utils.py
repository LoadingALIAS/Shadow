import tweepy
import re
import random
import database_utils
from datetime import datetime, timedelta

# Initialize Globals
logger = None
blocked_keywords = None
topics = None
query_terms = None

# Initialize Config
def initialize_configurations(loaded_logger, loaded_blocked_keywords, loaded_topics, loaded_query_terms):
    global logger, blocked_keywords, topics, query_terms
    logger = loaded_logger
    blocked_keywords = loaded_blocked_keywords
    topics = loaded_topics
    query_terms = loaded_query_terms

# Check for Blocked Keywords
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

# Follow a User from Timeline
def perform_follow(api):
    timeline = api.home_timeline(count=50)

    for tweet in timeline:
        user = tweet.user
        account_age = (datetime.now() - user.created_at).days
        if user.followers_count > 100 and account_age > 120:
            api.create_friendship(user.id)
            logger.info(f"Followed {user.screen_name}")

            # Update 'followed accounts' w/ Timestamp
            database_utils.add_followed_account(user.screen_name)

            break

# Unfollow a User by Rules
def perform_unfollow(api):
    # Load 'target list' from DB
    target_list = database_utils.get_all_target_accounts()

    # Get 'followed accounts' from DB
    followed_accounts = {account[0]: account[1] for account in database_utils.get_all_followed_accounts()}

    for friend in tweepy.Cursor(api.friends).items():
        if friend.screen_name not in target_list and not friend.following:
            follow_date_str = followed_accounts.get(friend.screen_name, '')
            if follow_date_str:
                follow_date = datetime.strptime(follow_date_str, '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.now() - follow_date).days >= 8:
                    api.destroy_friendship(friend.id)
                    logger.info(f"Unfollowed {friend.screen_name}")

                    # Remove from List in DB
                    database_utils.remove_followed_account(friend.screen_name)

                    break

# Retweet
def perform_retweet(api):
    random_topic = random.choice(topics)

    for tweet in search_tweets(api, 10):
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
    random_query = random.choice(query_terms)
    
    return tweepy.Cursor(api.search_tweets, random_query).items(max_tweets)

# Like
def perform_like(api):
    # Fetch 'target list' & 'following list'
    target_list = database_utils.get_all_target_accounts()
    following_list = database_utils.get_all_following_accounts()

    # Combine & Shuffle
    total_list = list(set(target_list + following_list))
    random.shuffle(total_list)

    # Select Random Accounts
    num_accounts_to_like = random.randint(1, min(8, len(total_list)))
    selected_accounts = random.sample(total_list, num_accounts_to_like)

    # Initialize 'Like' Count
    like_count = 0

    for account in selected_accounts:
        if like_count >= 8:
            break

        # Fetch User Tweets
        recent_tweets = api.user_timeline(screen_name=account, count=10)

        if not recent_tweets:
            continue

        # Like Random Tweet from User
        tweet_to_like = random.choice(recent_tweets)

        if not tweet_to_like.favorited:
            tweet_to_like.favorite()
            like_count += 1
            logger.info(f"Liked a tweet from {account}")