import time
import logging
import pytz
import re
import schedule
from datetime import datetime, timedelta
import configparser
import openai_utils
import twitter_utils
import random
import argparse
import content_utils
from flask import Flask, request, redirect
import threading
from tweepy import OAuthHandler, API

# Initialize Flask
app = Flask(__name__)

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize OAuth
auth = OAuthHandler(config.get('Twitter', 'CONSUMER_KEY'), config.get('Twitter', 'CONSUMER_SECRET'))

@app.route('/start_auth')
def start_auth():
    try:
        # Get the request tokens from Twitter
        redirect_url = auth.get_authorization_url()
        # Redirect user to Twitter to authorize
        return redirect(redirect_url)
    except Exception as e:
        logger.error(f"Failed to authenticate with Twitter: {e}")
        return "Failed to authenticate with Twitter."

@app.route('/twitter_callback', methods=['GET'])
def twitter_callback():
    oauth_verifier = request.args.get('oauth_verifier')
    if oauth_verifier:
        try:
            # Get the access token
            auth.get_access_token(oauth_verifier)
            # Initialize the Tweepy API
            api = API(auth)
            # Perform authenticated actions here, if needed
            return "OAuth verified."
        except Exception as e:
            logger.error(f"Failed to verify OAuth: {e}")
            return "Failed to verify OAuth."
    return "Missing OAuth verifier."

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSABI_Shadow_Bot")

# Set Timezone
tz = pytz.timezone('America/Los_Angeles')

# Read account type and set max tweet length
account_type = config['General']['ACCOUNT_TYPE']
max_tweet_length = 280 if account_type == 'free' else 4000

# Initialize CLI Arguments
parser = argparse.ArgumentParser(description='Control the Shadow Bot.')
parser.add_argument('--start', choices=['auto', 'schedule'], help='Start the bot in a specific mode.')
parser.add_argument('--schedule_time', type=str, help='Specify the schedule time in the format HH:MM-HH:MM.')
args = parser.parse_args()

# Validate 'start' argument
if args.start not in ['auto', 'schedule']:
    logger.error("Invalid value for --start. Choose between 'auto' and 'schedule'.")
    exit(1)

# Validate 'schedule_time' argument
if args.start == 'schedule':
    if not args.schedule_time:
        logger.error("--schedule_time is required when --start is 'schedule'.")
        exit(1)
    
    try:
        start_time, end_time = args.schedule_time.split('-')
        datetime.datetime.strptime(start_time, '%H:%M')  # Validates HH:MM format
        datetime.datetime.strptime(end_time, '%H:%M')  # Validates HH:MM format
    except ValueError:
        logger.error("Invalid --schedule_time format. Use HH:MM-HH:MM.")
        exit(1)

# Global variables to keep track of interaction counts and times
interaction_limits = {
    'tweet': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 4, 'period': timedelta(days=1)},
    'reply': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 16, 'period': timedelta(days=1)},
    'follow': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 16, 'period': timedelta(days=1)},
    'unfollow': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 16, 'period': timedelta(days=1)},
    'retweet': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 4, 'period': timedelta(days=1)}
}

# Check if an interaction can be performed
def can_perform_interaction(interaction_type):
    limit_info = interaction_limits[interaction_type]
    current_time = datetime.now(tz)
    if current_time - limit_info['last_time'] >= limit_info['period']:
        limit_info['last_time'] = current_time
        limit_info['count'] = 0  # Resetting the count
    return limit_info['count'] < limit_info['limit']

# Filter for Advertising, Promos, and Newsletters
def is_blocked_keyword_present(text, blocked_keywords):
    for keyword in blocked_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.I):
            return True
    return False

def perform_interaction(interaction_type, is_blocked_keyword_present, external_content=None, tweet_content=None):
    global max_tweet_length
    blocked_keywords = ['Ad', 'Promo', 'Advert', 'Advertisement', 'Promotion', 'Promotional', 'Newsletter']
    
    try:
        if can_perform_interaction(interaction_type):

            # Fetch random content if the interaction is a tweet
            if interaction_type in ['tweet']:
                external_content = content_utils.fetch_random_content()

            if interaction_type in ['reply', 'tweet']:
                # Check for blocked keywords in the tweet text and user screen name
                tweet_text = tweet_content.get('tweet_text', '') if tweet_content else ''
                user_screen_name = tweet_content.get('user_screen_name', '') if tweet_content else ''

                if not is_blocked_keyword_present(tweet_text, blocked_keywords) and not is_blocked_keyword_present(user_screen_name, blocked_keywords):
                    prompt = openai_utils.read_prompt(interaction_type)
                    encoded_prompt = f"{prompt}\n{external_content['content'] if external_content else tweet_content}"
                    reply_text = openai_utils.call_openai_api(encoded_prompt, max_tweet_length)

                    if interaction_type == 'reply':
                        twitter_utils.post_reply(user_screen_name, tweet_content['tweet_id'], reply_text)
                    else:
                        twitter_utils.post_tweet(reply_text)
                else:
                    logger.info(f"Skipped interaction with tweet or account from {user_screen_name} due to keyword restrictions.")
                    return  # Skip the rest of the function

            elif interaction_type == 'follow':
                twitter_utils.perform_follow()
            elif interaction_type == 'unfollow':
                twitter_utils.perform_unfollow()
            elif interaction_type == 'retweet':
                twitter_utils.perform_retweet(is_blocked_keyword_present)    

            # Update the count for the performed interaction
            interaction_limits[interaction_type]['count'] += 1
            
    except Exception as e:
        logger.error(f"Failed to perform {interaction_type}: {e}")

# Function to operate the bot in auto mode
def operate_in_auto_mode():
    actions = ['tweet', 'reply', 'follow', 'unfollow', 'retweet']
    chosen_action = random.choice(actions)
    
    if can_perform_interaction(chosen_action):
        perform_interaction(chosen_action)
        logger.info(f"Performed action: {chosen_action}")
    else:
        logger.info(f"Cannot perform action: {chosen_action}, limit reached.")

# Function to run Flask in a separate thread
def run_flask_app():
    app.run(port=80)

# Start Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.start()

# Your existing code for starting the bot in auto or schedule mode
if args.start == 'auto':
    while True:
        operate_in_auto_mode()
        sleep_time = random.randint(1, 3600)
        time.sleep(sleep_time)

if args.start == 'schedule':
    schedule.every().day.at(start_time).do(operate_in_auto_mode).tag('auto_mode')
    schedule.every().day.at(end_time).do(schedule.clear, 'auto_mode')

    while True:
        schedule.run_pending()
        time.sleep(1)

