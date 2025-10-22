#!/bin/bash
# Flask Web Application Startup Script

set -e  # Exit on any error

echo "Starting E-commerce Search Web Application"
echo "=============================================="

# Get the project root directory (parent of scripts/web)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

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

# Run the application
python scripts/web/run_web.py
