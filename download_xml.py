#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from pathlib import Path
from models import Aufmacher
from config import db


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

        r = requests.get(auf.unique_id)

        with open(xml_file_path, "w") as xml_file:
            xml_file.write(r.text)

    db.close()


if __name__ == "__main__":
    download()
