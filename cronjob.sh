#! /bin/bash

cd /home/jujulian/code/zcraper
source venv/bin/activate
python scrape.py
python bot.py
