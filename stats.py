#!/usr/bin/python
# -*- coding: utf-8 -*-

from peewee import *
from playhouse.shortcuts import model_to_dict
from models import Aufmacher, Author, Image
from config import db


def stats():
    db.connect()

    aufmacher_count = Aufmacher.select().count()
    author_count = Author.select().count()
    image_count = Image.select().count()

    print("Stats:")
    print("{:>5} Aufmacher".format(aufmacher_count))
    print("{:>5} authors".format(author_count))
    print("{:>5} images".format(image_count))

    print("\nLatest:")
    latest_aufmacher = Aufmacher.select().order_by(Aufmacher.created_at.desc())
    latest_aufmacher_string = """
since {created_at}
{supertitle}: {title}
{subtitle}
by {author_name}
    """.format(
        **model_to_dict(latest_aufmacher[0]),
        author_name=latest_aufmacher[0].author.name)
    print(latest_aufmacher_string.strip())


    db.close()


if __name__ == "__main__":
    stats()
