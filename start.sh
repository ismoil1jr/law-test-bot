#!/bin/bash
set -e

# Botni background da ishga tushirish va logga yozish
python -u bot.py > bot.log 2>&1 &

# Flask serverni ishga tushirish
gunicorn main:app -b 0.0.0.0:8000