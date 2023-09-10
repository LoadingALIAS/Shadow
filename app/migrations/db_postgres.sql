--
-- Table structure for table "follow"
--

CREATE TABLE "follow" (
  "id" SERIAL PRIMARY KEY,
  "userId" BIGINT NOT NULL,
  "userName" varchar(100) NOT NULL,
  "status" text,
  "followDate" TIMESTAMP WITH TIME ZONE NOT NULL,
  "unfollowDate" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  "lastAction" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ON "follow" ("userId");

--
-- Table structure for table "tweet"
--

CREATE TABLE "tweet" (
  "id" SERIAL PRIMARY KEY,
  "content" text NOT NULL,
  "date" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ON "tweet" ("content");

--
-- Table structure for table "reply"
--

CREATE TABLE "reply" (
  "id" SERIAL PRIMARY KEY,
  "userId" BIGINT NOT NULL,
  "userName" VARCHAR(100) NOT NULL,
  "tweetId" BIGINT NOT NULL,
  "status" TEXT NOT NULL,
  "answer" TEXT NOT NULL,
  "replyDate" TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ON "reply" ("tweetId");

--
-- Table structure for table "favorite"
--

CREATE TABLE "favorite" (
  "id" SERIAL PRIMARY KEY,
  "userId" BIGINT NOT NULL,
  "userName" VARCHAR(100) NOT NULL,
  "tweetId" BIGINT NOT NULL,
  "status" TEXT NOT NULL,
  "favDate" TIMESTAMP WITH TIME ZONE NOT NULL,
  "unfavDate" TIMESTAMP WITH TIME ZONE NULL,
  "lastAction" TIMESTAMP WITH TIME ZONE NOT NULL
);

--
-- Table structure for table "analytics"
--

CREATE TABLE "analytics" (
  "id" SERIAL PRIMARY KEY,
  "tweetImpressions" INT NOT NULL,
  "followersChange" REAL NOT NULL,
  "engagementRate" REAL NOT NULL,
  "linkClicks" INT NOT NULL,
  "rtsWithoutComments" INT NOT NULL,
  "likes" INT NOT NULL,
  "replies" INT NOT NULL,
  "captureDate" TIMESTAMP WITH TIME ZONE NOT NULL
);

--
-- Table structure for table "threads"
--

CREATE TABLE "threads" (
  "id" SERIAL PRIMARY KEY,
  "threadId" BIGINT NOT NULL,
  "tweetId" BIGINT NOT NULL,
  "date" TIMESTAMP WITH TIME ZONE NOT NULL
);

--
-- Table structure for table "polls"
--

CREATE TABLE "polls" (
  "id" SERIAL PRIMARY KEY,
  "pollId" BIGINT NOT NULL,
  "option" TEXT NOT NULL,
  "votes" INT NOT NULL
);
