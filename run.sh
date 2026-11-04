#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt > /dev/null
python3 src/main.py