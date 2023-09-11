package content

import (
	"bytes"
	"io"
	"log"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

type RedditContent struct {
	Url string
}

func (reddit RedditContent) callAPI() ([]Content, error) {
	resp, err := getWebserviceResponse(reddit.Url)
	if err != nil {
		log.Println("Error while calling URL: " + reddit.Url)
		return nil, err
	}
	defer resp.Body.Close() // Don't forget to close the response body

	var buf bytes.Buffer

	_, err = io.Copy(&buf, resp.Body)
	if err != nil {
		log.Println("Error while reading the response body")
		return nil, err
	}

	// Create a new reader with the buffer
	reader := bytes.NewReader(buf.Bytes())

	// Create a goquery document
	doc, err := goquery.NewDocumentFromReader(reader)
	if err != nil {
		log.Println("Error while creating the goquery document")
		return nil, err
	}

	rv := make([]Content, 0)

	doc.Find("div.Post").Each(func(i int, selec *goquery.Selection) {
		// ignore sticky posts
		if selec.HasClass("stickied") {
			return
		}

		if len(rv) > 20 {
			return
		}

		t := selec.Find("h3")
		title := t.First().Find("span").First().Text()

		// Limit size of content
		if len(title)+urlLength > 280 {
			title = title[0:279-urlLength] + "…"
		}

		l := selec.Find("a[target=\"_blank\"]")
		externalLink, _ := l.First().Attr("href")

		// self posts
		if strings.HasPrefix(externalLink, "/r/") {
			externalLink = "https://reddit.com" + externalLink
		}

		rv = append(rv, Content{
			Text: title,
			Url:  externalLink,
		})
	})

	return rv, nil
}
