#!/bin/bash

cd /home/jasonandmonte/projects/aggregator
git pull

source env/bin/activate
python3 src/scraper.py > ../index.html
deactivate

git add .
git commit -m "Automated update"
git push
