import time
import logging
import pytz
import json
import schedule
from datetime import datetime, timedelta
import configparser
import openai_utils
import twitter_utils
import random
import argparse

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# Set Timezone
tz = pytz.timezone('America/Los_Angeles')

# Read account type and set max tweet length
account_type = config['General']['ACCOUNT_TYPE']
max_tweet_length = 280 if account_type == 'free' else 4000

# Initialize CLI Arguments
parser = argparse.ArgumentParser(description='Control your Twitter bot.')
parser.add_argument('--start', choices=['auto', 'schedule'], help='Start the bot in a specific mode.')
parser.add_argument('--schedule_time', type=str, help='Specify the schedule time in the format HH:MM-HH:MM.')
parser.add_argument('--analytics', action='store_true', help='Show analytics.')
args = parser.parse_args()

# Global variables to keep track of interaction counts and times
interaction_limits = {
    'thread': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 1, 'period': timedelta(weeks=1)},
    'tweet': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 4, 'period': timedelta(days=1)},
    'reply': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 32, 'period': timedelta(days=1)},
    'follow': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 16, 'period': timedelta(days=1)},
    'unfollow': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 16, 'period': timedelta(days=1)},
    'retweet': {'count': 0, 'last_time': datetime.min.replace(tzinfo=tz), 'limit': 4, 'period': timedelta(days=1)}
}

# Check if an interaction can be performed
def can_perform_interaction(interaction_type):
    limit_info = interaction_limits[interaction_type]
    if datetime.now(tz) - limit_info['last_time'] >= limit_info['period']:
        limit_info['last_time'] = datetime.now(tz)
        limit_info['count'] = 0
    return limit_info['count'] < limit_info['limit']

# Perform an interaction
def perform_interaction(interaction_type, external_content=None, tweet_content=None):
    global max_tweet_length
    if can_perform_interaction(interaction_type):
        if interaction_type in ['reply', 'tweet', 'thread']:
            prompt = openai_utils.read_prompt(interaction_type)
            encoded_prompt = f"{prompt}\n{external_content if interaction_type in ['thread', 'tweet'] else tweet_content}"
            reply_text = openai_utils.call_openai_api(encoded_prompt, max_tweet_length)
            
            if interaction_type == 'reply':
                twitter_utils.post_reply(tweet_content['user_screen_name'], tweet_content['tweet_id'], reply_text)
            else:
                twitter_utils.post_tweet(reply_text)
        elif interaction_type == 'follow':
            twitter_utils.perform_follow()
        elif interaction_type == 'unfollow':
            twitter_utils.perform_unfollow()
        elif interaction_type == 'retweet':
            twitter_utils.perform_retweet()

        # Update the count for the performed interaction
        interaction_limits[interaction_type]['count'] += 1

# Function to operate the bot in auto mode
def operate_in_auto_mode():
    actions = ['tweet', 'reply', 'thread', 'follow', 'unfollow', 'retweet']
    chosen_action = random.choice(actions)
    
    if can_perform_interaction(chosen_action):
        perform_interaction(chosen_action)
        logger.info(f"Performed action: {chosen_action}")
    else:
        logger.info(f"Cannot perform action: {chosen_action}, limit reached.")

# Handling CLI arguments
if args.start == 'auto':
    while True:
        operate_in_auto_mode()
        sleep_time = random.randint(1, 3600)
        time.sleep(sleep_time)

elif args.start == 'schedule':
    schedule_time = args.schedule_time.split('-')
    schedule.every().day.at(schedule_time[0]).do(operate_in_auto_mode).tag('auto_mode')
    if len(schedule_time) == 2:
        schedule.every().day.at(schedule_time[1]).do(schedule.clear, 'auto_mode')

    while True:
        schedule.run_pending()
        time.sleep(1)

if args.stop:
    schedule.clear('auto_mode')

if args.analytics:
    analytics_data = twitter_utils.get_analytics()
    print("Twitter Analytics:")
    for key, value in analytics_data.items():
        print(f"{key}: {value}")
