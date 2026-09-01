#!/bin/bash
set -e

echo "🚀 Starting bot..."
python -u bot.py &

echo "🚀 Starting Flask server..."
gunicorn main:app -b 0.0.0.0:${PORT:-8000}