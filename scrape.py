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
from models import Aufmacher, Author, Image
from config import db
import untangle


DOWNLOAD_URL = "http://www.zeit.de"


def get_article_data(unique_id):
    r = requests.get(unique_id)
    obj = untangle.parse(r.text)
    article = obj.article
    head = obj.article.head
    body = obj.article.body

    author_unique_id = head.author["href"]
    author_name = head.author.display_name.cdata.strip()
    author_image_id = head.author.image["base-id"].strip()
    author_image_copyright = head.author.image.copyright.cdata.strip()

    supertitle = body.supertitle.cdata.strip()
    title = body.title.cdata.strip()
    subtitle = body.subtitle.cdata.strip()

    image_id = head.image["base-id"].strip()
    image_copyright = head.image.copyright.cdata.strip()
    image_caption = head.image.bu.cdata.strip()

    first_released = None
    for attribute in head.attribute:
        if attribute["name"] == "date_first_released":
            first_released = arrow.get(attribute.cdata).datetime

    author = Author.get_or_create(
        unique_id=author_unique_id,
        defaults={
            "name": author_name
        })

    if author[1]:
        author_image = Image.get_or_create(
            unique_id=author_image_id,
            defaults={
                "copyright": author_image_copyright
            })
        author[0].image = author_image[0]
        author[0].save()

    article_image = None
    if image_id and len(image_id):
        article_image = Image.get_or_create(
            unique_id=image_id,
            defaults={
                "copyright": image_copyright,
                "caption": image_caption
            })[0]

    aufmacher = Aufmacher.create(
        unique_id=unique_id,
        supertitle=supertitle,
        title=title,
        subtitle=subtitle,
        first_released=first_released,
        author=author[0],
        image=article_image)

    return aufmacher



def scrape():
    r = requests.get(DOWNLOAD_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    teaser = soup.select(".teaser-fullwidth")[0]
    unique_id = teaser["data-unique-id"].strip()


    db.connect()
    db.create_tables([Image, Author, Aufmacher], safe=True)


    latest_aufmacher_id = None
    latest_aufmacher = Aufmacher.select().order_by(Aufmacher.created_at.desc()).limit(1)

    if len(latest_aufmacher):
        latest_aufmacher_id = latest_aufmacher[0].unique_id

    if latest_aufmacher_id != unique_id:
        aufmacher = get_article_data(unique_id)


    db.close()


if __name__ == "__main__":
    scrape()
