#!/bin/bash

cd /home/jasonandmonte/projects/aggregator
git pull

echo "Starting scrape"
/home/jasonandmonte/projects/aggregator/env/bin/python3 src/scraper.py > ./index.html
echo "Committing"

git add .
git commit -m "Automated update"
git push
