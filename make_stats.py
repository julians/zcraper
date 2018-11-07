import untangle
import requests
from models import Aufmacher, Author, Image, TweetJob
from config import db
import csv
from pathlib import Path
import arrow
from collections import defaultdict

dumb_tag_list = []
all_tags = {}


def get_tags(article_xml):
    head = article_xml.head

    try:
        tags = head.rankedTags
    except AttributeError:
        return []

    saved_tags = []
    for tag in tags.tag:
        tag_name = tag.cdata.strip()
        tag_type = tag["type"]

        saved_tags.append({"name": tag_name, "type": tag_type})

        key = tag_name + tag_type
        if not key in all_tags:
            all_tags[key] = {"name": tag_name, "type": tag_type, "count": 0}

        all_tags[key]["count"] += 1

        dumb_tag_list.append(tag_name)

    return saved_tags


def get_article_data(aufmacher, article_xml):
    tags = get_tags(article_xml)

    created = arrow.get(aufmacher.created_at)
    release_date = created.format("YYYY-MM-DD")
    release_time = created.format("HH-mm-ss")

    url_parts = aufmacher.unique_id.replace("http://xml.zeit.de/", "").split("/")

    breaking_news = False
    text_length = None
    for attribute in article_xml.head.attribute:
        if attribute["name"] == "breaking_news":
            if attribute.cdata == "yes":
                breaking_news = True
        if attribute["name"] == "text-length":
            try:
                text_length = int(attribute.cdata)
            except Exception:
                text_length = None

    return {
        "url": aufmacher.unique_id,
        "tags": ",".join([x["name"] for x in tags]),
        "releaseDate": release_date,
        "releaseTime": release_time,
        "title": aufmacher.title,
        "superTitle": aufmacher.supertitle,
        "ressort": url_parts[0],
        "subressort": url_parts[1],
        "breaking": breaking_news,
        "textLength": text_length,
        "questionMarkInTitle": "?" in aufmacher.title,
        "exclamationMarkInTitle": "?" in aufmacher.title,
        "numberOfQuotationMarksInTitle": aufmacher.title.count('"'),
    }


def make_stats():
    start_date = arrow.get("2017-11-06", "YYYY-MM-DD").datetime
    end_date = arrow.get("2018-11-05", "YYYY-MM-DD").datetime
    number_of_days = (end_date - start_date).days

    db.connect()
    aufmacher = (
        Aufmacher.select()
        .where(
            (Aufmacher.created_at >= start_date) & (Aufmacher.created_at <= end_date)
        )
        .order_by(Aufmacher.created_at)
    )
    csv_data = []

    print("{} Aufmacher an {} Tagen".format(len(aufmacher), number_of_days))
    print(len(aufmacher) / number_of_days, " Aufmacher pro Tag")

    for auf in aufmacher:
        path_to_file = auf.unique_id.replace("http://xml.zeit.de/", "")
        xml_file_path = (Path("xml") / path_to_file).with_suffix(".xml")

        if xml_file_path.is_file():
            with open(xml_file_path, "r") as xml_file:
                parsed_article = untangle.parse(xml_file)
                article_data = get_article_data(auf, parsed_article.article)

                if article_data:
                    csv_data.append(article_data)

    with open("stats/aufmacher.csv", "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)

    with open("stats/tags.csv", "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(all_tags.values())[0].keys())
        writer.writeheader()
        writer.writerows(all_tags.values())

    with open("stats/tagcloud.txt", "w") as out_file:
        out_file.write("\n".join(dumb_tag_list))


if __name__ == "__main__":
    make_stats()
