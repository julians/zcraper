#! /bin/bash

script_path="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $script_path

source venv/bin/activate
python scrape.py
python bot.py
