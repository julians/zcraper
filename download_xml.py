#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from pathlib import Path
from models import Aufmacher
from config import db
import untangle


def download_article(unique_id):
    print("download {}".format(unique_id))
    r = requests.get(unique_id)

    if r.text.startswith("<?xml", 0, 5):
        article_xml = untangle.parse(r.text)

        try:
            url = article_xml.link.body.url.cdata.strip()
            url = url.replace("http://www.zeit.de", "http://xml.zeit.de").replace(
                "https://www.zeit.de", "http://xml.zeit.de"
            )
            print("url", url)
            return download_article(url)
        except AttributeError:
            return r.text
    else:
        return None


def download():
    db.connect()
    aufmacher = Aufmacher.select()
    aufmacher_length = len(aufmacher)

    for index, auf in enumerate(aufmacher):
        path_to_file = auf.unique_id.replace("http://xml.zeit.de/", "")
        xml_file_path = (Path("xml") / path_to_file).with_suffix(".xml")
        if xml_file_path.is_file():
            continue

        print("{}/{}".format(index, aufmacher_length), xml_file_path)

        folder = xml_file_path.parent
        Path(folder).mkdir(parents=True, exist_ok=True)

        article_content = download_article(auf.unique_id)
        if article_content:
            print("writing", xml_file_path)
            with open(xml_file_path, "w") as xml_file:
                xml_file.write(article_content)
        else:
            print("error!")

    db.close()


if __name__ == "__main__":
    download()
