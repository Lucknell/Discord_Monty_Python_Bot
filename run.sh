#!/bin/bash

export QUART_APP=server:app
exec python3 -u -m quart  run --host=0.0.0.0 -p 5101 &
exec python3 -u /src/bot/monty.py
