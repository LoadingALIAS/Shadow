package db

import (
	"database/sql"
	"fmt"

	"github.com/LoadingALIAS/Shadow/app/config"
	_ "github.com/lib/pq"
)

var database *sql.DB

func Init() (*sql.DB, error) {
	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		config.PG_HOST, config.PG_PORT, config.PG_USER, config.PG_PASSWORD, config.PG_DBNAME)

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
