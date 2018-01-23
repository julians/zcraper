#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
import datetime
import os
import os.path
import requests
import json
from models import Aufmacher, Author, Image, TweetJob
from config import db
from playhouse.shortcuts import model_to_dict

from secrets import twitter_secrets


def tweet(tweetjob):
    href = tweetjob.aufmacher.unique_id.replace("http://xml", "http://www")
    tweet_text = """
{supertitle}: {title}
{subtitle}
    """.format(**model_to_dict(tweetjob.aufmacher)).strip()

    if len(tweet_text) > 250:
        tweet_text = "{:.250}…".format(tweet_text)

    tweet = """
{tweet_text}
{href}
    """.format(tweet_text=tweet_text,
        href=href).strip()

    auth = tweepy.OAuthHandler(twitter_secrets["CONSUMER_KEY"], twitter_secrets["CONSUMER_SECRET"])
    auth.set_access_token(twitter_secrets["ACCESS_TOKEN"], twitter_secrets["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)
    api.update_status(status=tweet)

    tweetjob.tweeted_at = datetime.datetime.now()
    tweetjob.save()


def go():
    tweetjobs = TweetJob.select().where(TweetJob.tweeted_at == None)

    for tweetjob in tweetjobs:
        tweet(tweetjob)





if __name__ == "__main__":
    go()


#     #media_upload_response = api.media_upload(image_filename)
#     #print(media_upload_response.media_id_string)
#     #api.update_status(status="test with image", media_ids=[media_upload_response.media_id_string])

#     with open("last_tweeted", 'w') as file:
#         file.write(todays_date)
