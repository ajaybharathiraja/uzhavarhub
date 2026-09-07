#!/bin/bash
python3.9 -m pip install -r requirements.txt --break-system-packages || python3 -m pip install -r requirements.txt --break-system-packages
python3.9 manage.py collectstatic --noinput --clear || python3 manage.py collectstatic --noinput --clear
