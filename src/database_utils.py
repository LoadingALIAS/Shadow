import sqlite3
from datetime import datetime

# Initialize
def initialize_db():
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS followed_accounts
                        (screen_name TEXT PRIMARY KEY, follow_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS target_accounts
                        (screen_name TEXT PRIMARY KEY)''')  # New Table
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Followed
def add_followed_account(screen_name):
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO followed_accounts VALUES (?, ?)", (screen_name, str(datetime.now())))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Unfollowed
def remove_followed_account(screen_name):
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM followed_accounts WHERE screen_name = ?", (screen_name,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# All Followed Accounts
def get_all_followed_accounts():
    accounts = []
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            for row in c.execute('SELECT * FROM followed_accounts'):
                accounts.append(row)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return accounts

# Add Target Accounts
def add_target_account(screen_name):
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO target_accounts VALUES (?)", (screen_name,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Remove Target Accounts
def remove_target_account(screen_name):
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM target_accounts WHERE screen_name = ?", (screen_name,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# All Target Accounts
def get_all_target_accounts():
    accounts = []
    try:
        with sqlite3.connect('Shadow_Bot.db') as conn:
            c = conn.cursor()
            for row in c.execute('SELECT * FROM target_accounts'):
                accounts.append(row[0])
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return accounts
