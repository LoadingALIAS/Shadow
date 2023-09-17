import praw 
import feedparser
import random
import datetime
import logging
from time import mktime
from bs4 import BeautifulSoup

# Globals 
logger = None
reddit = None

# Initialize Config
def initialize_configurations(loaded_logger, loaded_reddit_config):
    global logger, reddit
    logger = loaded_logger

    # Initialize Reddit API with OAuth
    reddit = praw.Reddit(
        client_id=loaded_reddit_config['CLIENT_ID'],
        client_secret=loaded_reddit_config['CLIENT_SECRET'],
        user_agent=loaded_reddit_config['USER_AGENT'],
        username=loaded_reddit_config['USERNAME'],
        password=loaded_reddit_config['PASSWORD']
    )

# Fetch Reddit Content
def fetch_reddit_content():
    try:
        subreddits = ['ArtificialInteligence', 'LocalLLaMA', 'MachineLearning', 'machinelearningnews']
        selected_subreddit = random.choice(subreddits)
        fetched_post = {}
        sub = reddit.subreddit(selected_subreddit)
        top_posts = [post for post in sub.hot(limit=10)]
        selected_post = random.choice(top_posts)
        fetched_post = {
            'source': 'Reddit',
            'title': selected_post.title,
            'description': selected_post.selftext,
            'score': selected_post.score,
            'timestamp': datetime.datetime.fromtimestamp(selected_post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        }
        return fetched_post
    except Exception as e:
        print(f"Error fetching Reddit content: {e}")
        return None

# Fetch DailyAI Content
def fetch_dailyai_content():
    feed = feedparser.parse("https://dailyai.com/feed")
    sorted_articles = sorted(feed['entries'], key=lambda x: mktime(x['published_parsed']), reverse=True)
    top_articles = sorted_articles[:4]
    selected_article = random.choice(top_articles)
    content_encoded = selected_article.get('content', [{'value': 'N/A'}])[0]['value']
    soup = BeautifulSoup(content_encoded, 'html.parser')
    content_encoded = soup.get_text()
    fetched_article = {
        'source': 'DailyAI',
        'title': selected_article.get('title', 'N/A'),
        'description': selected_article.get('description', 'N/A'),
        'content': content_encoded
    }
    return fetched_article

# Fetch at Random
def fetch_random_content():
    content = None
    try:
        # Random Choice
        selected_source = random.choice([fetch_reddit_content, fetch_dailyai_content])
        
        # Fetch Content
        content = selected_source()
        
    except Exception as e:
        logging.exception(f"An error occurred while fetching content from {selected_source.__name__}: {e}")
        selected_source = fetch_reddit_content

    if content is None or not content:
        logging.error(f"Failed to fetch content from {selected_source.__name__}. Falling back to Reddit.")
        content = fetch_reddit_content()

    return content