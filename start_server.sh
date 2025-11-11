#!/bin/bash
#
# Startup script for Reddit Sentiment MCP Server
# This starts the local server - you need to run ngrok separately
#

set -e

echo "============================================================"
echo "Starting Reddit Sentiment MCP Server"
echo "============================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first to create the virtual environment"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Create a .env file with your Reddit API credentials:"
    echo ""
    echo "REDDIT_CLIENT_ID=your_client_id"
    echo "REDDIT_CLIENT_SECRET=your_client_secret"
    echo "REDDIT_USERNAME=your_username"
    echo "REDDIT_PASSWORD=your_password"
    echo ""
    echo "Continuing anyway (some features may not work)..."
    echo ""
fi

# Start the server
echo "🚀 Starting MCP server on http://localhost:8000..."
echo ""
echo "============================================================"
echo "SERVER URLS:"
echo "============================================================"
echo "Local:  http://localhost:8000"
echo "Docs:   http://localhost:8000/docs"
echo "Health: http://localhost:8000/health"
echo "============================================================"
echo ""
echo "⚠️  IMPORTANT: To connect to n8n online, you need ngrok!"
echo ""
echo "In a SEPARATE terminal, run:"
echo "  ngrok http 8000"
echo ""
echo "Then use the ngrok HTTPS URL in your n8n workflows"
echo "============================================================"
echo ""

python src/mcp_server.py
