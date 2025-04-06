#!/bin/bash

cd /home/jasonandmonte/projects/aggregator
git pull

echo "Starting scrape"
source env/bin/activate
python3 src/scraper.py > ../index.html
deactivate
echo "Committing"

git add .
git commit -m "Automated update"
git push
