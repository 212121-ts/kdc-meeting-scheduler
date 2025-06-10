#!/bin/bash

# Render.com startup script for KDC Meeting Scheduler

echo "🚀 Starting KDC Meeting Scheduler on Render..."

# Set environment variable to indicate we're on Render
export RENDER=true

# Ensure templates are created before starting gunicorn
echo "🎨 Ensuring templates are created..."
python -c "
import app
app.create_templates()
app.init_db()
print('✅ Templates and database initialized')
"

# Start the application with gunicorn
echo "🌐 Starting web server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app