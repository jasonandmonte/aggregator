#!/bin/bash

source env/bin/activate
python3 src/scraper.py > ../index.html
deactivate
