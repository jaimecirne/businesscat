#!/bin/bash
source /opt/poetry-venv/bin/activate
poetry install 
which python
python businesscat/bcat_main.py