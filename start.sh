#!/bin/bash

# Render.com startup script for KDC Meeting Scheduler

echo "🚀 Starting KDC Meeting Scheduler on Render..."

# Set environment variable to indicate we're on Render
export RENDER=true

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app