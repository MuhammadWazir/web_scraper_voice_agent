#!/bin/sh

# Start the application
echo "Starting Voice Agent application..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800 --limit-concurrency 100
