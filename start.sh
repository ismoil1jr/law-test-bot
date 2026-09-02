#!/bin/bash
set -e

echo "🚀 Starting Flask App & Telegram Bot..."
exec gunicorn app:app -b 0.0.0.0:${PORT:-8000} --workers 1