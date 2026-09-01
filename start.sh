#!/bin/bash
# Flask server va botni bir vaqtda ishga tushirish

# Botni background da ishga tushirish
python bot.py &

# Flask serverni ishga tushirish (gunicorn)
gunicorn main:app -b 0.0.0.0:8000