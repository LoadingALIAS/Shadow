import sqlite3
from datetime import datetime

# Initialize Logging
logger = None

# Initialize Config
def initialize_configurations(loaded_logger):
    global logger
    logger = loaded_logger

# Initialize DB Connection
conn = sqlite3.connect('Shadow_Bot.db')
c = conn.cursor()

# Initialize DB
def initialize_db():
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS followed_accounts
                    (screen_name TEXT PRIMARY KEY, follow_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS target_accounts
                    (screen_name TEXT PRIMARY KEY)''')
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

# Add Followed Account
def add_followed_account(screen_name):
    try:
        c.execute("INSERT INTO followed_accounts VALUES (?, ?)", (screen_name, str(datetime.now())))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

# Remove Followed Account
def remove_followed_account(screen_name):
    try:
        c.execute("DELETE FROM followed_accounts WHERE screen_name = ?", (screen_name,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

# Get all Followed Accounts
def get_all_followed_accounts():
    accounts = []
    try:
        for row in c.execute('SELECT * FROM followed_accounts'):
            accounts.append(row)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    return accounts

# Add Target
def add_target_account(screen_name):
    try:
        c.execute("INSERT INTO target_accounts VALUES (?)", (screen_name,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

# Remove Target Accounnts
def remove_target_account(screen_name):
    try:
        c.execute("DELETE FROM target_accounts WHERE screen_name = ?", (screen_name,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

# Get all Target Accounts
def get_all_target_accounts():
    accounts = []
    try:
        for row in c.execute('SELECT * FROM target_accounts'):
            accounts.append(row[0])
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    return accounts

# Get all Following Accounts 
def get_all_following_accounts():
    accounts = []
    try:
        for row in c.execute('SELECT screen_name FROM followed_accounts'):
            accounts.append(row[0])
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    return accounts