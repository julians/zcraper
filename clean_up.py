#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import os.path
from peewee import *
from models import Aufmacher, Author, Image, TweetJob
from config import db
from playhouse.shortcuts import model_to_dict



def clean_up():
    db.connect()

    aufmachers = Aufmacher\
        .select(Aufmacher, TweetJob)\
        .join(TweetJob, JOIN.LEFT_OUTER, on=(Aufmacher.id == TweetJob.aufmacher).alias('tweetjob'))\
        .order_by(Aufmacher.created_at.desc())

    for aufmacher in aufmachers:
        if not aufmacher.tweetjob.id:
            print(model_to_dict(aufmacher.tweetjob))
            aufmacher.tweetjob.save()


    db.close()


if __name__ == "__main__":
    clean_up()
