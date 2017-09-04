#!/usr/bin/python
# -*- coding: utf-8 -*-

from peewee import *
from config import db
import datetime


class Image(Model):
    unique_id = CharField()
    copyright = CharField()
    caption = TextField(null = True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Author(Model):
    unique_id = CharField()
    name = CharField()
    image = ForeignKeyField(Image, null = True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Aufmacher(Model):
    unique_id = CharField()
    supertitle = CharField()
    title = CharField()
    subtitle = TextField()
    first_released = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    author = ForeignKeyField(Author)
    image = ForeignKeyField(Image, null = True)

    class Meta:
        database = db
