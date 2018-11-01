#!/usr/bin/python
# -*- coding: utf-8 -*-

from peewee import *
from config import db
import datetime


class Base(Model):
    class Meta:
        database = db


class Image(Base):
    unique_id = CharField()
    copyright = CharField()
    caption = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class Author(Base):
    unique_id = CharField()
    name = CharField()
    image = ForeignKeyField(Image, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class Aufmacher(Base):
    unique_id = CharField()
    supertitle = CharField()
    title = CharField()
    subtitle = TextField()
    first_released = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    image = ForeignKeyField(Image, null=True)

    class Meta:
        database = db

    def get_url(self):
        return self.unique_id.replace("http://xml.zeit.de", "https://www.zeit.de")

    def get_mail_teaser_image(self):
        image_url = self.image.unique_id.replace(
            "http://xml.zeit.de", "https://img.zeit.de"
        )
        return "{}wide__250x141__desktop".format(image_url)


class AufmacherAuthor(Base):
    aufmacher = ForeignKeyField(Aufmacher)
    author = ForeignKeyField(Author)


class TweetJob(Base):
    aufmacher = ForeignKeyField(Aufmacher)
    tweeted_at = DateTimeField(null=True)
