package db

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
	// Import conf.go here
)

var database *sql.DB

func Init() (*sql.DB, error) {
	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DBNAME)

	// Init Postgres DB
	dbLink, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	// Validate DSN data
	err = dbLink.Ping()
	if err != nil {
		return nil, err
	}

	// Set up global var
	database = dbLink

	return database, nil
}
