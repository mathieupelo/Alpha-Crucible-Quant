#!/bin/bash
# Ngrok startup script for Linux/Mac
# This script starts Ngrok tunnel for Alpha Crucible Quant

echo "Starting Ngrok tunnel for Alpha Crucible Quant..."
echo

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found in project root!"
    echo "Please copy .env_template to .env and configure your settings."
    echo "Current directory: $(pwd)"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check if auth token is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "Error: NGROK_AUTHTOKEN not found in .env file!"
    exit 1
fi

# Configure Ngrok auth token
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Start Ngrok tunnel
echo "Starting Ngrok tunnel on port 80..."
echo "Your app will be accessible via the public URL shown below."
echo
ngrok http 80
