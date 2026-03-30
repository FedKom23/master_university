import os
import io
import json

import boto3
import pandas as pd
import clickhouse_connect
import redis
import requests

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://localhost:19000")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "edu")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio123")

CH_HOST = os.environ.get("CH_HOST", "localhost")
CH_PORT = int(os.environ.get("CH_PORT", "8123"))

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)

client = clickhouse_connect.get_client(
    host=CH_HOST,
    port=CH_PORT
)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
)

with open("hw3/example_data/init.sql", "r") as f:
    init_sql = f.read()

with open("hw3/example_data/events_example.json", "r") as f:
    json_data = f.read()

old_text = "FROM file('events_example.json', 'JSONEachRow');"
new_text = "FORMAT JSONEachRow"
init_sql_v2 = init_sql.replace(old_text, new_text)
first_quers = init_sql_v2.split(";")

for query in first_quers[:-1]:
    if query.strip():
        client.command(query.strip())

requests.post(
    f"http://{CH_HOST}:{CH_PORT}/",
    params={
        'query': first_quers[-1],
    },
    data=json_data,
)

q1 = client.query_df("""
WITH daily_platform AS (
    SELECT
        event_date,
        platform,
        countIf(event = 'impression')    AS impressions,
        countIf(event = 'click')         AS clicks,
        countIf(event = 'purchase')      AS purchases,
        sumIf(price, event = 'purchase') AS revenue,
        countDistinct(user_id)           AS uniq_users
    FROM mydb.events
    GROUP BY event_date, platform
),
campaign_revenue AS (
    SELECT
        event_date,
        platform,
        campaign_id,
        sumIf(price, event = 'purchase') AS camp_revenue
    FROM mydb.events
    GROUP BY event_date, platform, campaign_id
),
campaign_ranked AS (
    SELECT
        event_date,
        platform,
        camp_revenue,
        row_number() OVER (
            PARTITION BY event_date, platform
            ORDER BY camp_revenue DESC
        ) AS rnk
    FROM campaign_revenue
),
top3 AS (
    SELECT
        event_date,
        platform,
        sum(camp_revenue) AS revenue_top3
    FROM campaign_ranked
    WHERE rnk <= 3
    GROUP BY event_date, platform
),
pre_res AS (
    SELECT
        dp.event_date,
        dp.platform,
        dp.impressions,
        dp.clicks,
        dp.purchases,
        dp.revenue,
        dp.uniq_users,
        dp.clicks    / nullIf(dp.impressions, 0)        AS ctr,
        dp.purchases / nullIf(dp.clicks, 0)             AS cr,
        dp.revenue   / nullIf(dp.impressions, 0) * 1000 AS cpm,
        sum(dp.revenue) OVER (
            PARTITION BY dp.platform
            ORDER BY dp.event_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        )                                                AS rev_3d,
        t3.revenue_top3 / nullIf(dp.revenue, 0)         AS top3_rev_share
    FROM daily_platform dp
    JOIN top3 t3 ON dp.event_date = t3.event_date AND dp.platform = t3.platform
    ORDER BY dp.event_date, dp.platform
)
SELECT
    event_date,
    platform,
    impressions,
    clicks,
    purchases,
    revenue,
    uniq_users,
    ROUND(ctr, 2)               AS ctr,
    COALESCE(cr, 0)             AS cr,
    ROUND(cpm, 2)               AS cpm,
    rev_3d,
    COALESCE(top3_rev_share, 0) AS top3_rev_share
FROM pre_res
ORDER BY event_date, platform
""")

r.flushall()
for _, row in q1.iterrows():
    mapping = {k: str(v) for k, v in row.to_dict().items()}
    mapping.pop("event_date")
    mapping.pop("platform")
    key = f"hw3:q1:{row['event_date'].strftime('%Y-%m-%d')}:{row['platform']}"
    r.set(key, json.dumps(mapping))

client.command("""
CREATE TABLE IF NOT EXISTS mydb.campaigns (
    campaign_id  UInt32,
    category     String,
    region       String,
    is_brand     UInt8,
    budget_daily Float64,
    start_date   Date,
    end_date     Date
) ENGINE = MergeTree()
ORDER BY campaign_id
""")

obj = s3.get_object(Bucket=MINIO_BUCKET, Key="campaigns.csv")
campaigns_df = pd.read_csv(io.BytesIO(obj["Body"].read()))
campaigns_df["start_date"] = pd.to_datetime(campaigns_df["start_date"]).dt.date
campaigns_df["end_date"] = pd.to_datetime(campaigns_df["end_date"]).dt.date
client.command("TRUNCATE TABLE mydb.campaigns")
client.insert_df("mydb.campaigns", campaigns_df)

q2 = client.query_df("""
WITH campaign_metrics AS (
    SELECT
        campaign_id,
        sumIf(price, event = 'purchase') AS camp_revenue
    FROM mydb.events
    GROUP BY campaign_id
),
joined AS (
    SELECT
        c.category,
        c.region,
        cm.campaign_id,
        c.is_brand,
        cm.camp_revenue
    FROM campaign_metrics cm
    JOIN mydb.campaigns c ON c.campaign_id = cm.campaign_id
)
SELECT
    category,
    region,
    sum(camp_revenue) AS revenue,
    uniqExact(campaign_id) AS campaigns,
    ifNull(
        sumIf(camp_revenue, is_brand = 1) / nullIf(sum(camp_revenue), 0),
        0
    ) AS brand_revenue_share,
    argMax(campaign_id, camp_revenue) AS top_campaign_id,
    max(camp_revenue) AS top_campaign_revenue
FROM joined
GROUP BY category, region
ORDER BY category, region
""")

for _, row in q2.iterrows():
    mapping = {k: str(v) for k, v in row.to_dict().items()}
    mapping.pop("category")
    mapping.pop("region")
    key = f"hw3:q2:{row['category']}:{row['region']}"
    r.set(key, json.dumps(mapping))
