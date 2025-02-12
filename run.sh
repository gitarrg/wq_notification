#!/bin/bash

cd /home/me/wow/wow_notifications

source venv/bin/activate

export WEBHOOK_URL="<insert URL>"

python main.py
