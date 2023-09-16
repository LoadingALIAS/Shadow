import time
import logging
import re
import schedule
import configparser
import argparse
import random
import threading

from flask import Flask, request, redirect
from tweepy import OAuthHandler, API
from threading import Lock
from datetime import datetime, timedelta

# Initialize Flask
app = Flask(__name__)

# Initialize Lock
interaction_lock = Lock()

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSABI_Shadow_Bot")

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# ---- Start of Configuration Validation ----
REQUIRED_SECTIONS = {
    "General": ["ACCOUNT_TYPE", "NGROK_DOMAIN"],
    "Search": ["QUERY", "MAX_TWEETS"],
    "Topics": ["TOPICS"],
    "Twitter": ["CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"],
    "OpenAI": ["API_KEY", "MODEL", "TEMPERATURE", "MAX_TOKENS", "PRESENCE_PENALTY", "FREQUENCY_PENALTY"],
    "Reddit": ["CLIENT_ID", "CLIENT_SECRET", "USER_AGENT", "USERNAME", "PASSWORD"],
    "InteractionLimits": ["tweet_limit", "reply_limit", "follow_limit", "unfollow_limit", "retweet_limit", "like_limit"],
    "Keywords": ["blocked_keywords"]
}

for section, keys in REQUIRED_SECTIONS.items():
    if not config.has_section(section):
        logger.error(f"Missing section: {section} in config.ini")
        exit(1)
    for key in keys:
        if not config.has_option(section, key):
            logger.error(f"Missing key: {key} in section: {section} in config.ini")
            exit(1)
# ---- End of Configuration Validation ----

# Initialize OAuth
auth = OAuthHandler(config.get('Twitter', 'CONSUMER_KEY'), config.get('Twitter', 'CONSUMER_SECRET'))

# Declare API Variable
api = None

# Route Start
@app.route('/start_auth', methods=['GET'])
def start_auth():
    global auth
    try:
        # Get Request Tokens
        redirect_url = auth.get_authorization_url()
        # Redirect to Twitter for Auth
        return redirect(redirect_url)
    except Exception as e:
        logger.error(f"Failed to start OAuth: {e}")
        return "Failed to start OAuth."

# Route Twitter Callback
@app.route('/twitter_callback', methods=['GET'])
def twitter_callback():
    global api 
    oauth_verifier = request.args.get('oauth_verifier')
    if oauth_verifier:
        try:
            # Get Access Token
            auth.get_access_token(oauth_verifier)
            
            # Save Access Token/Secret
            config.set('Twitter', 'ACCESS_TOKEN', auth.access_token)
            config.set('Twitter', 'ACCESS_TOKEN_SECRET', auth.access_token_secret)
            
            # Optional: Save the new config to config.ini
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            # Initialize Tweepy w/ New Tokens
            api = API(auth)
            
            return "OAuth verified."
        except Exception as e:
            logger.error(f"Failed to verify OAuth: {e}")
            return "Failed to verify OAuth."
    return "Missing OAuth verifier."

# Read Account Type to Set Max Length
account_type = config['General']['ACCOUNT_TYPE']
max_tweet_length = 280 if account_type == 'free' else 4000

# Initialize Modules
import database_utils 
import openai_utils
import twitter_utils
import content_utils

# Extract and Pass Config to Modules
blocked_keywords = [keyword.strip() for keyword in config.get('Keywords', 'blocked_keywords').split(',')]
topics = config.get('Topics', 'TOPICS').split(', ')
query_terms = config.get('Search', 'QUERY').split(', ')
reddit_config = {key: config.get('Reddit', key) for key in ['CLIENT_ID', 'CLIENT_SECRET', 'USER_AGENT', 'USERNAME', 'PASSWORD']}
openai_params = {key: config.get('OpenAI', key) for key in ['API_KEY', 'MODEL', 'TEMPERATURE', 'MAX_TOKENS', 'PRESENCE_PENALTY', 'FREQUENCY_PENALTY']}

database_utils.initialize_configurations(logger)
openai_utils.initialize_configurations(logger, max_tweet_length, openai_params)
twitter_utils.initialize_configurations(logger, blocked_keywords, topics, query_terms)
content_utils.initialize_configurations(logger, reddit_config)

# Initialize DB
database_utils.initialize_db()

# Initialize CLI Arguments
parser = argparse.ArgumentParser(description='Control the Shadow Bot.')
parser.add_argument('--start', choices=['auto', 'schedule'], help='Start the bot in a specific mode.')
parser.add_argument('--schedule_time', type=str, help='Specify the schedule time in the format HH:MM-HH:MM.')
args = parser.parse_args()

# Validate 'start' argument
if args.start not in ['auto', 'schedule']:
    logger.error("Invalid value for --start. Choose between 'auto' and 'schedule'.")
    exit(1)

# Start OAuth process
try:
    # Manually visit this URL to start the OAuth process
    oauth_start_url = f"http://{config.get('General', 'NGROK_DOMAIN')}/start_auth"
    print(f"Visit this URL to start the OAuth process: {oauth_start_url}")
except Exception as e:
    logger.error(f"Failed to generate OAuth start URL: {e}")
    exit(1)

# Validate 'schedule_time' argument
if args.start == 'schedule':
    if not args.schedule_time:
        logger.error("--schedule_time is required when --start is 'schedule'.")
        exit(1)
    
    try:
        start_time, end_time = args.schedule_time.split('-')
        datetime.datetime.strptime(start_time, '%H:%M')
        datetime.datetime.strptime(end_time, '%H:%M')
    except ValueError:
        logger.error("Invalid --schedule_time format. Use HH:MM-HH:MM.")
        exit(1)

# Global Variables for Interactions - Count & Time
interaction_limits = {
    'like': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'like_limit')), 'period': timedelta(days=1)},
    'tweet': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'tweet_limit')), 'period': timedelta(days=1)},
    'reply': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'reply_limit')), 'period': timedelta(days=1)},
    'follow': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'follow_limit')), 'period': timedelta(days=1)},
    'unfollow': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'unfollow_limit')), 'period': timedelta(days=1)},
    'retweet': {'count': 0, 'last_time': datetime.min, 'limit': int(config.get('InteractionLimits', 'retweet_limit')), 'period': timedelta(days=1)}
}

# Check if Interaction can be Performed
def can_perform_interaction(interaction_type):
    with interaction_lock:  # Use the lock here
        limit_info = interaction_limits[interaction_type]
        current_time = datetime.now()
        if current_time - limit_info['last_time'] >= limit_info['period']:
            limit_info['last_time'] = current_time
            limit_info['count'] = 0  # Reset
        return limit_info['count'] < limit_info['limit']

# Check for Blocked Keywords
def is_blocked_keyword_present(text, blocked_keywords):
    for keyword in blocked_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.I):
            return True
    return False

# Main Interaction Function
def perform_interaction(interaction_type, external_content=None, tweet_content=None):
    global max_tweet_length
    
    try:
        if can_perform_interaction(interaction_type):

            # Fetch Content at Random
            if interaction_type == 'tweet':
                external_content = content_utils.fetch_random_content()

            if interaction_type in ['reply', 'tweet']:
                prompt = openai_utils.read_prompt(interaction_type)
                encoded_prompt = f"{prompt}\n{external_content['content'] if external_content else tweet_content}"
                reply_text = openai_utils.call_openai_api(encoded_prompt, max_tweet_length, logger)

                if interaction_type == 'reply':
                    twitter_utils.post_reply(api, tweet_content['user_screen_name'], tweet_content['tweet_id'], reply_text)
                else:
                    twitter_utils.post_tweet(api, reply_text)

            elif interaction_type == 'follow':
                twitter_utils.perform_follow(api)
            elif interaction_type == 'unfollow':
                twitter_utils.perform_unfollow(api)
            elif interaction_type == 'retweet':
                twitter_utils.perform_retweet(api)    

            # Update the Count for Performed Interaction
            interaction_limits[interaction_type]['count'] += 1
            
    except Exception as e:
        logger.error(f"Failed to perform {interaction_type}: {e}")

# Auto Mode Function
# main.py
def operate_in_auto_mode():
    actions = ['tweet', 'follow', 'unfollow', 'retweet', 'like', 'like', 'like', 'like']
    random.shuffle(actions)

    for chosen_action in actions:
        if can_perform_interaction(chosen_action):
            perform_interaction(chosen_action)
            logger.info(f"Performed action: {chosen_action}")
        else:
            logger.info(f"Cannot perform action: {chosen_action}, limit reached.")

# Function for Flask Thread
def run_flask_app():
    app.run(port=80)

# Start Flask in Separate Thread
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.start()

# Start Shadow Bot in Auto/Schedule Mode
if args.start == 'auto':
    while True:
        operate_in_auto_mode()
        sleep_time = random.randint(1, 3600)
        time.sleep(sleep_time)

if args.start == 'schedule':
    schedule.every().day.at(start_time).do(operate_in_auto_mode).tag('auto_mode')
    schedule.every().day.at(end_time).do(lambda: schedule.clear('auto_mode'))

    while True:
        schedule.run_pending()
        time.sleep(1)