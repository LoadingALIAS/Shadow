package main

import (
	"github.com/ChimeraCoder/anaconda"
	"github.com/jsgoecke/go-wit"
	"log"
	"math/rand"
	"strings"
)

const (
	INTENT_HI           = "hi"
	INTENT_NICE_ARTICLE = "nice_article"
	INTENT_THANK_FOLLOW = "thank_follow"
)

func buildReply(tweet anaconda.Tweet) (string, error) {
	message := cleanTweetMessage(tweet.Text)
	if message == "" {
		return "", nil
	}

	// Process a text message
	request := &wit.MessageRequest{}
	request.Query = message

	result, err := witclient.Message(request)
	if err != nil {
		return "", err
	}

	// TODO(remy): quick fix
	if len(result.Outcomes) == 0 {
		return "", nil
	}

	outcome := result.Outcomes[0]
	intent := outcome.Intent
	if outcome.Confidence < 0.5 {
		log.Println("Not enough confidence for intent : " + intent)
		return "", nil
	}

	if intent == INTENT_HI {
		return buildHiIntentResponse(tweet), nil
	} else if intent == INTENT_NICE_ARTICLE {
		return buildNiceArticleIntentResponse(tweet), nil
	} else if intent == INTENT_THANK_FOLLOW {
		return buildThanksFollowIntentResponse(tweet), nil
	}

	return "", nil
}

func buildHiIntentResponse(tweet anaconda.Tweet) string {
	greetings := []string{"hello!", "hey", "yo"}

	return buildMention(tweet.User, greetings[rand.Intn(len(greetings))])
}

func buildNiceArticleIntentResponse(tweet anaconda.Tweet) string {
	greetings := []string{"hello!", "hey", "hi", "well,", ""}
	thanks := []string{"thanks", "thank you", "many thanks", "thx"}
	messages := []string{"reading", "your tweet", "your message"}

	greet := greetings[rand.Intn(len(greetings))]
	thank := thanks[rand.Intn(len(thanks))]
	message := messages[rand.Intn(len(messages))]

	return buildMention(tweet.User, greet+" "+thank+" for "+message)
}

func buildThanksFollowIntentResponse(tweet anaconda.Tweet) string {
	greetings := []string{"hello!", "hey", "hi", "well,", ""}
	thanks := []string{"thanks", "thank you", "many thanks", "thx"}
	follows := []string{"following me", "the follow"}
	messages := []string{"your message", "your tweet", "your mention"}
	reciprocals := []string{"too", "as well", ""}

	following, err := isUserFollowing(tweet.User.ScreenName)
	if following && err == nil {
		greet := greetings[rand.Intn(len(greetings))]
		thank := thanks[rand.Intn(len(thanks))]
		follow := follows[rand.Intn(len(follows))]
		reciprocal := reciprocals[rand.Intn(len(reciprocals))]

		return buildMention(tweet.User, greet+" "+thank+" for "+follow+" "+reciprocal)
	} else {
		greet := greetings[rand.Intn(len(greetings))]
		thank := thanks[rand.Intn(len(thanks))]
		message := messages[rand.Intn(len(messages))]

		return buildMention(tweet.User, greet+" "+thank+" for "+message)
	}
}

func buildMention(user anaconda.User, text string) string {
	return "@" + user.ScreenName + " " + text
}

func cleanTweetMessage(message string) string {
	cleaned := ""

	words := strings.Split(message, " ")
	for _, word := range words {
		if strings.HasPrefix(word, "@") || strings.HasPrefix(word, "http") {
			continue
		} else if strings.HasPrefix(word, "#") {
			cleaned += strings.TrimPrefix(word, "#") + " "
		}

		cleaned += word + " "
	}

	return cleaned
}
