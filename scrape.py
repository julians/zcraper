#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import os.path
import requests
import json
from bs4 import BeautifulSoup
import arrow
from peewee import *
from models import Aufmacher, Author, Image, TweetJob
from config import db
import untangle


DOWNLOAD_URL = "http://www.zeit.de"


def get_article_data(unique_id):
    obj = untangle.parse(unique_id)

    try:
        article = obj.article
    except AttributeError:
        try:
            article = obj.link
        except AttributeError:
            article = obj.gallery

    head = article.head
    body = article.body

    # author_unique_id = head.author["href"]
    # author_name = head.author.display_name.cdata.strip()
    # author_image_id = head.author.image["base-id"].strip()
    # author_image_copyright = head.author.image.copyright.cdata.strip()

    supertitle = body.supertitle.cdata.strip()
    title = body.title.cdata.strip()
    subtitle = body.subtitle.cdata.strip()

    try:
        image_id = head.image["base-id"].strip()
        image_copyright = head.image.copyright.cdata.strip()
        image_caption = head.image.bu.cdata.strip()
    except AttributeError:
        image_id = None

    first_released = None
    for attribute in head.attribute:
        if attribute["name"] == "date_first_released":
            first_released = arrow.get(attribute.cdata).datetime

    # author = Author.get_or_create(
    #    unique_id=author_unique_id,
    #    defaults={
    #        "name": author_name
    #    })
    #
    # if author[1]:
    #    author_image = Image.get_or_create(
    #        unique_id=author_image_id,
    #        defaults={
    #            "copyright": author_image_copyright
    #        })
    #    author[0].image = author_image[0]
    #    author[0].save()

    article_image = None
    if image_id and len(image_id):
        article_image = Image.get_or_create(
            unique_id=image_id,
            defaults={"copyright": image_copyright, "caption": image_caption},
        )[0]

    aufmacher = Aufmacher.create(
        unique_id=unique_id,
        supertitle=supertitle,
        title=title,
        subtitle=subtitle,
        first_released=first_released,
        # author=author[0],
        image=article_image,
    )

    tweet_job = TweetJob.create(aufmacher=aufmacher)

    return aufmacher


def scrape():
    r = requests.get(DOWNLOAD_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    teaser = soup.select(".teaser-fullwidth")
    if not len(teaser):
        teaser = soup.select(".teaser-classic")

    if len(teaser):
        teaser = teaser[0]
    else:
        return

    unique_id = teaser["data-unique-id"].strip().replace("https", "http")

    db.connect()
    db.create_tables([Image, Author, Aufmacher, TweetJob], safe=True)

    possible_duplicate = Aufmacher.select().where(Aufmacher.unique_id == unique_id)
    if not len(possible_duplicate):
        aufmacher = get_article_data(unique_id)

    db.close()


if __name__ == "__main__":
    scrape()
