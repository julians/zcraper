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
from models import Aufmacher, Author, Image, TweetJob, AufmacherAuthor
from config import db
import untangle


DOWNLOAD_URL = "http://www.zeit.de"


def get_author_data(unique_id=None, article=None):
    if not article:
        obj = untangle.parse(
            "http://xml.zeit.de/gesellschaft/2018-07/flucht-migration-mittelmeer-syrien-deutschland"
        )

        try:
            article = obj.article
        except AttributeError:
            article = obj.link

    head = article.head

    authors = head.author
    print(len(authors))
    saved_authors = []

    for author in authors:
        author_name = author.display_name.cdata.strip()
        author_unique_id = author["href"]

        print(author_name)

        saved_author, author_created = Author.get_or_create(
            unique_id=author_unique_id, defaults={"name": author_name}
        )

        if saved_author:
            try:
                author_image_id = author.image["base-id"].strip()
            except AttributeError:
                author_image_id = None

            if author_image_id:
                print(author_image_id)
                author_image_copyright = author.image.copyright.cdata.strip()

                author_image, image_created = Image.get_or_create(
                    unique_id=author_image_id,
                    defaults={"copyright": author_image_copyright},
                )

                if image_created:
                    saved_author.image = author_image
                    saved_author.save()

        saved_authors.append(saved_author)

    return saved_authors


def get_article_data(unique_id):
    obj = untangle.parse(unique_id)
    # obj = untangle.parse(
    #     "http://xml.zeit.de/gesellschaft/2018-07/flucht-migration-mittelmeer-syrien-deutschland"
    # )

    try:
        article = obj.article
    except AttributeError:
        article = obj.link

    head = article.head
    body = article.body

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
        image=article_image,
    )

    TweetJob.create(aufmacher=aufmacher)

    authors = get_author_data(article)
    if len(authors):
        for author in authors:
            AufmacherAuthor.create(aufmacher=aufmacher, author=author)

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

    # unique_id = teaser["data-unique-id"].strip().replace("https", "http")

    unique_id = "http://xml.zeit.de/gesellschaft/2018-07/flucht-migration-mittelmeer-syrien-deutschland"

    db.connect()
    db.create_tables([Image, Author, Aufmacher, TweetJob, AufmacherAuthor], safe=True)

    possible_duplicate = Aufmacher.select().where(Aufmacher.unique_id == unique_id)
    if True or not len(possible_duplicate):
        aufmacher = get_article_data(unique_id)

    db.close()


if __name__ == "__main__":
    scrape()
