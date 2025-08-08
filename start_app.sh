#!/bin/bash

# AdCP Agent Platform - Startup Script

echo "🚀 Starting AdCP Agent Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the Flask app
echo "🌐 Starting Flask app on http://localhost:5001..."
echo "📊 Health check: http://localhost:5001/api/health"
echo "🎯 Main app: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
