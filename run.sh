#!/bin/bash

export QUART_APP=server:app
exec /venv/bin/python3 -u -m quart  run --host=0.0.0.0 -p 5101 &
exec /venv/bin/python3 -u /src/bot/monty.py
