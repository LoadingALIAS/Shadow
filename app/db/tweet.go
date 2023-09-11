package db

import (
	"time"
)

type Tweet struct {
	ID      int
	Content string
	Date    time.Time
}

const (
	_TABLE_TWEET = "tweet"
)

func (tweet Tweet) Persist() error {
	stmtIns, err := database.Prepare("INSERT INTO " + _TABLE_TWEET + "(content, date) VALUES( $1, $2 )")
	if err != nil {
		return err
	}

	defer stmtIns.Close()

	pacificTime := tweet.Date.In(location) // Using location from db.go
	_, err = stmtIns.Exec(tweet.Content, pacificTime)
	return err
}

func HasTweetWithContent(content string) (bool, error) {
	stmtOut, err := database.Prepare("SELECT count(*) FROM " + _TABLE_TWEET + " WHERE content LIKE $1 LIMIT 1")
	if err != nil {
		return true, err
	}

	defer stmtOut.Close()

	var size int

	err = stmtOut.QueryRow(content + "%").Scan(&size)
	if err != nil {
		return true, err
	}

	return size > 0, nil
}

func GetNumberOfTweetsBetweenDates(from time.Time, to time.Time) (int, error) {
	stmtOut, err := database.Prepare("SELECT count(*) FROM " + _TABLE_TWEET + " WHERE date >= $1 AND date <= $2 LIMIT 1")
	if err != nil {
		return 0, err
	}

	defer stmtOut.Close()

	var size int

	err = stmtOut.QueryRow(from, to).Scan(&size)
	if err != nil {
		return 0, err
	}

	return size, nil
}
