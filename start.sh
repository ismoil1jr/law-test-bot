#!/bin/bash
set -e

# Botni background da ishga tushirish
python bot.py &

# Flask serverni ishga tushirish
gunicorn main:app -b 0.0.0.0:8000