#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import os.path
from models import Aufmacher, Author, Image
from config import db
from jinja2 import Template


def go():
    select_from_datetime = datetime.datetime.now() - datetime.timedelta(days=1)
    db.connect()

    new_aufmachers = Aufmacher.select()\
        .where(Aufmacher.first_released > select_from_datetime)

    with open("mail_template.jinja2") as template_file:
        mail_template = Template(template_file.read())
        print(mail_template.render({
            "aufmacher": new_aufmachers,
            "date": datetime.datetime.now(),
        }))



if __name__ == "__main__":
    go()