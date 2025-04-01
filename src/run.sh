#!/bin/bash

cd /home/jasonandmonte/projects/aggregator
source env/bin/activate
python3 src/scraper.py > ../index.html
deactivate
