#!/bin/bash
LOCKFILE="/tmp/osint_scrape.lock"
(
flock -n 200 || exit 1
cd /home/dietpi/admindash-osint

git pull origin main
python3 osint_scraper.py

# Subir datos
git add data/*.csv
git commit -m "Update OSINT $(date +%F)"
git push origin main
) 200>$LOCKFILE
