#!/bin/bash
pip install -r requirements.txt
gunicorn --config gunicorn_config.py run:app