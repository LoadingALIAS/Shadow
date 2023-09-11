package main

import (
	"log"
	"net/url"
	"strings"
	"time"

	"github.com/ChimeraCoder/anaconda"
	"github.com/LoadingALIAS/Shadow/app/config"
	"github.com/LoadingALIAS/Shadow/app/db"
)

func stringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

func isUserFollowing(userName string) (bool, error) {
	friendships, err := api.GetFriendshipsLookup(url.Values{"screen_name": []string{userName}})
	if err != nil {
		log.Println("Error while querying twitter api for friendships", err)
		return false, err
	}

	following := false
	for _, friendship := range friendships {
		if stringInSlice("followed_by", friendship.Connections) {
			following = true
		}
	}

	return following, nil
}

func isUserAcceptable(tweet anaconda.Tweet) bool {
	words := strings.Split(tweet.Text, " ")
	for _, word := range words {
		if stringInSlice(strings.ToLower(word), config.BANNED_KEYWORDS) {
			return false
		}
	}

	if tweet.User.Description == "" {
		return false
	}

	words = strings.Split(tweet.User.Description, " ")
	for _, word := range words {
		if stringInSlice(strings.ToLower(word), config.BANNED_KEYWORDS) {
			return false
		}
	}

	return true
}

func generateAPISearchValues(word string) (string, url.Values) {
	searchString := word

	for _, word := range config.BANNED_KEYWORDS {
		searchString += " -" + word
	}

	v := url.Values{}
	v.Add("lang", config.ACCEPTED_LANGUAGE)
	v.Add("count", "100")
	v.Add("result_type", "recent")

	return url.QueryEscape(searchString), v
}

func isMentionOrRT(tweet anaconda.Tweet) bool {
	return strings.HasPrefix(tweet.Text, "RT") || strings.HasPrefix(tweet.Text, "@")
}

func isMe(tweet anaconda.Tweet) bool {
	return strings.ToLower(tweet.User.ScreenName) == strings.ToLower(config.USER_NAME)
}

func hasReachDailyTweetLimit() (bool, error) {
	var from time.Time
	var to time.Time

	now := time.Now()

	if now.Hour() >= config.WAKE_UP_HOUR {
		from = time.Date(now.Year(), now.Month(), now.Day(), config.WAKE_UP_HOUR, 0, 0, 0, now.Location())
	} else {
		yesterday := now.Add(-time.Duration(24) * time.Hour)
		from = time.Date(yesterday.Year(), yesterday.Month(), yesterday.Day(), config.WAKE_UP_HOUR, 0, 0, 0, yesterday.Location())
	}

	if now.Hour() < config.GO_TO_BED_HOUR {
		to = time.Date(now.Year(), now.Month(), now.Day(), config.GO_TO_BED_HOUR, 0, 0, 0, now.Location())
	} else {
		tomorrow := now.Add(time.Duration(24) * time.Hour)
		to = time.Date(tomorrow.Year(), tomorrow.Month(), tomorrow.Day(), config.GO_TO_BED_HOUR, 0, 0, 0, tomorrow.Location())
	}

	count, err := db.GetNumberOfTweetsBetweenDates(from, to)
	if err != nil {
		return true, err
	}

	return count >= config.MAX_TWEET_IN_A_DAY, nil
}
