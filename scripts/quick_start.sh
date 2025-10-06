#!/bin/bash
# Alpha Crucible Quant - Quick Start Script for Linux/Mac
# This script sets up and deploys the application in one go

echo "Alpha Crucible Quant - Quick Start"
echo "================================="
echo

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if .env file exists, if not copy from template
if [ ! -f .env ]; then
    echo "Setting up environment configuration..."
    cp .env_template .env
    echo
    echo "IMPORTANT: Please review and update the .env file with your settings!"
    echo "The template contains your Supabase credentials but you may need to adjust them."
    echo
    read -p "Press Enter to continue after reviewing the .env file..."
fi

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "Error: Docker is not running or not installed!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "Starting deployment..."
echo

# Deploy the application
./scripts/deploy.sh

echo
echo "Deployment completed!"
echo
echo "Next steps:"
echo "1. For external access, run: ./scripts/start_ngrok.sh"
echo "2. Your app will be available at the Ngrok URL shown"
echo "3. To view logs: docker-compose logs -f"
echo
