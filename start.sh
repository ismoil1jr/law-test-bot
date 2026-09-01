#!/bin/bash
# Flask serverni ishga tushirish (gunicorn)
gunicorn main:app -b 0.0.0.0:8000 &
# Botni ishga tushirish
python bot.py