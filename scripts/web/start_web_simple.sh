#!/bin/bash
# Simple Flask Web Application Startup Script (avoids lxml issues)

set -e  # Exit on any error

echo "Starting E-commerce Search Web Application (Simple Mode)"
echo "=========================================================="

# Get the project root directory (parent of scripts/web)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found. Using system Python."
fi

# Set environment variables
export FLASK_APP=scripts/web/run_web.py
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
export FLASK_ENV=development
export FLASK_HOST=127.0.0.1
export FLASK_PORT=5000
export FLASK_DEBUG=true

echo "Starting web server..."
echo "URL: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop"
echo ""

# Run the application directly (skip pip install to avoid lxml issues)
python scripts/web/run_web.py
