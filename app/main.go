package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	"github.com/ChimeraCoder/anaconda"
	"github.com/LoadingALIAS/Shadow/app/config"
	"github.com/LoadingALIAS/Shadow/app/content"
	"github.com/LoadingALIAS/Shadow/app/db"
	wit "github.com/jsgoecke/go-wit"
)

var api *anaconda.TwitterApi
var witclient *wit.Client

func main() {
	// Init Twitter API
	anaconda.SetConsumerKey(config.CONSUMER_KEY)
	anaconda.SetConsumerSecret(config.CONSUMER_SECRET)
	api = anaconda.NewTwitterApi(config.TOKEN, config.TOKEN_SECRET)

	// Init DB
	database, err := db.Init()
	if err != nil {
		panic(err.Error())
	}

	defer database.Close()

	// Init Content
	content.Init(config.HASHTAGS, config.T_CO_URL_LENGTH)

	for _, kimonoDataSourcesUrl := range config.KIMONO_DATA_SOURCES {
		content.RegisterAPI(content.KimonoContent{Url: kimonoDataSourcesUrl})
	}

	for _, redditDataSourceUrl := range config.REDDIT_DATA_SOURCES {
		content.RegisterAPI(content.RedditContent{Url: redditDataSourceUrl})
	}

	// Init WIT api
	witclient = wit.NewClient(config.WIT_ACCESS_TOKEN)

	// Init random
	rand.Seed(time.Now().UnixNano())

	// Starts the wake up ticker
	var d time.Duration
	if d, err = time.ParseDuration(config.ACTIONS_INTERVAL); err != nil {
		panic(fmt.Sprintf("Can't parse as duration the ACTIONS_INTERVAL config value: %s", config.ACTIONS_INTERVAL))
	}

	ticker := time.NewTicker(d)

	log.Println("Hello world")

	// do a first launch for immediate action before starting the ticker
	bot()

	// wake up and go to sleep forever ever and never. tintintin.
	for range ticker.C {
		bot()
	}
}

func bot() {
	log.Println("----------- Waking up!")

	hour := time.Now().Hour()

	if config.GO_TO_BED_HOUR < config.WAKE_UP_HOUR && (hour >= config.WAKE_UP_HOUR || hour < config.GO_TO_BED_HOUR) {
		performDailyAction()
	} else if config.GO_TO_BED_HOUR > config.WAKE_UP_HOUR && (hour >= config.WAKE_UP_HOUR && hour < config.GO_TO_BED_HOUR) {
		performDailyAction()
	} else {
		performNightlyAction()
	}

	log.Println("----------- Goes to sleep")
}
