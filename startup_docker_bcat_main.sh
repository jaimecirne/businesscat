#!/bin/bash
poetry install
poetry run /usr/bin/env .venv/bin/python businesscat/bcat_main.py