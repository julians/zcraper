#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import os.path
from jinja2 import Template
import sendgrid
import arrow
import subprocess
import os

from models import Aufmacher, Author, Image
from config import db
from secrets import sendgrid_key


send = False

current_dir = os.getcwd()

def go():
    select_from_datetime = datetime.datetime.now() - datetime.timedelta(days=1)
    db.connect()

    new_aufmachers = Aufmacher.select()\
        .where(Aufmacher.first_released > select_from_datetime)

    date_string = arrow.now().format('D. MMMM YYYY', locale='de')
    subject = "ZON zum {}".format(date_string)

    mail_html = None
    mail_text = None

    with open("mail_template.jinja2") as mjml_template_file:
        mail_mjml_template = Template(mjml_template_file.read())
        mail_mjml = mail_mjml_template.render({
            "aufmacher": new_aufmachers,
            "subject": subject,
            "date_string": date_string,
        })

    with open("text_template.jinja2") as text_template_file:
        mail_text_template = Template(text_template_file.read())
        mail_text = mail_text_template.render({
            "aufmacher": new_aufmachers,
            "subject": subject,
            "date_string": date_string,
        })

    if mail_mjml:
        mjml_filename = os.path.join(current_dir, "tmp/mail.mjml")
        mjmp_exec_path = os.path.join(current_dir, "node_modules/.bin/mjml")

        try:
            os.remove(mjml_filename)
        except OSError:
            pass
        with open(mjml_filename, "w") as mjml_output_file:
            mjml_output_file.write(mail_mjml)

        try:
            mail_html = subprocess.check_output([mjmp_exec_path, mjml_filename])
            mail_html = mail_html.decode("utf-8")
        except subprocess.CalledProcessError:
            mail_html = None

        try:
            os.remove(mjml_filename)
        except OSError:
            pass


    if mail_html and mail_text and send:
        sg = sendgrid.SendGridAPIClient(sendgrid_key)
        data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": "hello@julianstahnke.com"
                        }
                    ],
                    "subject": subject
                }
            ],
            "from": {
                "email": "hello@julianstahnke.com"
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": "and easy to do anywhere, even with Python"
                },
                {
                    "type": "text/html",
                    "value": mail_html
                }
            ]
        }
        response = sg.client.mail.send.post(request_body=data)
        print(response.status_code)
        print(response.body)
        print(response.headers)



if __name__ == "__main__":
    go()