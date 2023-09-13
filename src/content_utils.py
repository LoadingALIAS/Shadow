import praw  # For Reddit
import feedparser  # For RSS feeds
import configparser  # For reading API keys from config.ini
import random
import datetime
import logging
from time import mktime
from bs4 import BeautifulSoup

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize Reddit API with OAuth
reddit = praw.Reddit(
    client_id=config['Reddit']['CLIENT_ID'],
    client_secret=config['Reddit']['CLIENT_SECRET'],
    user_agent=config['Reddit']['USER_AGENT'],
    username=config['Reddit']['USERNAME'],
    password=config['Reddit']['PASSWORD']
)

def fetch_reddit_content():
    subreddits = ['ArtificialIntelligence', 'LocalLLaMA', 'MachineLearning']
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

def fetch_random_content():
    content = None
    try:
        # Randomly choose between Reddit and DailyAI
        selected_source = random.choice([fetch_reddit_content, fetch_dailyai_content])
        
        # Fetch content from the selected source
        content = selected_source()
        
    except Exception as e:
        logging.error(f"An error occurred while fetching content from {selected_source.__name__}: {e}")
        selected_source = fetch_reddit_content  # Fallback to Reddit

    if content is None or not content:
        # Log an error or fallback to Reddit
        logging.error(f"Failed to fetch content from {selected_source.__name__}. Falling back to Reddit.")
        content = fetch_reddit_content()

    return content

# Example usage
if __name__ == "__main__":
    fetched_content = fetch_random_content()
    print("Fetched Content Details:")
    print(fetched_content)
