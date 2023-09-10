package config

import "os"

var (
  // Load all your variables here
  UserName = os.Getenv("USER_NAME")

//const USER_NAME = "twitterName"
//const ACTIONS_INTERVAL = "30m"
//const WAKE_UP_HOUR int = 16
//const GO_TO_BED_HOUR int = 8

//const CONSUMER_KEY string = ""
//const CONSUMER_SECRET string = ""
//const TOKEN string = ""
//const TOKEN_SECRET string = ""
//const DEBUG_TWITTER bool = false

//const WIT_ACCESS_TOKEN string = ""

//const ACTION_FOLLOW_WEIGHT int = 1
//const ACTION_UNFOLLOW_WEIGHT int = 1
//const ACTION_FAVORITE_WEIGHT int = 1
//const ACTION_UNFAVORITE_WEIGHT int = 1
//const ACTION_TWEET_WEIGHT int = 1
//const ACTION_REPLY_WEIGHT int = 1
//const ACTION_NIGHTLY_FOLLOW_WEIGHT int = 1
//const ACTION_NIGHTLY_UNFOLLOW_WEIGHT int = 1
//const ACTION_NIGHTLY_FAVORITE_WEIGHT int = 1
//const ACTION_NIGHTLY_UNFAVORITE_WEIGHT int = 1
//const ACTION_NIGHTLY_TWEET_WEIGHT int = 1
//const ACTION_NIGHTLY_REPLY_WEIGHT int = 1
//const FAV_LIMIT_IN_A_ROW int = 5
//const UNFOLLOW_LIMIT_IN_A_ROW int = 5
//const UNFAVORITE_LIMIT_IN_A_ROW int = 1
//const MAX_TWEET_IN_A_DAY int = 5

//const T_CO_URL_LENGTH = 25

//const MYSQL_USER string = ""
//const MYSQL_PASSWORD string = ""
//const MYSQL_SCHEMA string = "/db"

//const PG_HOST string = "localhost"
//const PG_PORT int = 5432
//const PG_USER string = ""
//const PG_PASSWORD string = ""
//const PG_DBNAME string = ""

//var KIMONO_DATA_SOURCES = []string{"https://www.kimonolabs.com/api", "https://www.kimonolabs.com/api"}
//var REDDIT_DATA_SOURCES = []string{}
//var KEYWORDS = []string{"key1", "key2}
//var HASHTAGS = []string{"hash1", "hash2"}

//const ACCEPTED_LANGUAGE string = "en"

//var BANNED_KEYWORDS = []string{"porn"}
