import argparse
import json
import logging
import os

import tweepy
from dotenv import load_dotenv
from tweet_counter import count_tweet

load_dotenv()


CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]


# Authenticate to Twitter
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
)
auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_KEY,
    ACCESS_SECRET,
)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True)


logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
logger = logging.getLogger(__name__)


def tweet_thread(thread_data, base_path):
    for index, tweet in enumerate(thread_data, start=1):
        tweet_length = count_tweet(tweet["content"])
        if tweet_length > 280:
            raise ValueError(
                f"Tweet number {index} exceeds 280 characters by {tweet_length - 280}. Content: {tweet['content']}"
            )

    # Posting the thread
    previous_tweet_id = None
    for tweet_data in thread_data:
        if "media" in tweet_data and tweet_data["media"]:
            media_ids = [
                api.media_upload(os.path.join(base_path, media["path"])).media_id
                for media in tweet_data["media"]
            ]
        else:
            media_ids = None

        # Post tweet
        if previous_tweet_id is None:
            # First tweet of the thread
            tweet = client.create_tweet(text=tweet_data["content"], media_ids=media_ids)
        else:
            # Subsequent tweets in the thread
            tweet = client.create_tweet(
                text=tweet_data["content"],
                in_reply_to_tweet_id=previous_tweet_id,
                media_ids=media_ids,
            )

        previous_tweet_id = tweet.data["id"]
        logger.info(f"Tweeted: {tweet_data['content']}")

    logger.info("Thread posted!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tweet a thread from a json file.")
    parser.add_argument(
        "file", type=str, help="Path to the json file containing the thread data."
    )
    args = parser.parse_args()

    with open(args.file, "r") as f:
        thread_data = json.load(f)

    base_path = os.path.dirname(os.path.abspath(args.file))
    tweet_thread(thread_data, base_path)
