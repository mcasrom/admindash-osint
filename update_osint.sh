#!/bin/bash
cd /home/dietpi/admindash-osint
source venv/bin/activate
python3 osint_scraper.py
# matar streamlit viejo si hay
pkill -f "streamlit run dashboard.py"
# lanzar dashboard en segundo plano
nohup streamlit run dashboard.py --server.port 8501 --server.headless true > logs/dashboard.log 2>&1 &
