CREATE DATABASE IF NOT EXISTS mydb;

CREATE TABLE IF NOT EXISTS mydb.events
(
    event_time  DateTime,
    event_date  Date,
    user_id     UInt64,
    campaign_id UInt64,
    event       LowCardinality(String),
    price       Float64,
    platform    LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, campaign_id, platform, event_time);

INSERT INTO mydb.events
SELECT
    parseDateTimeBestEffort(event_time) AS event_time,
    toDate(event_date) AS event_date,
    toUInt64(user_id) AS user_id,
    toUInt64(campaign_id) AS campaign_id,
    toString(event) AS event,
    toFloat64(price) AS price,
    toString(platform) AS platform
FROM file('events_example.json', 'JSONEachRow');