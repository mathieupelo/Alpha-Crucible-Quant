#!/bin/bash
# Alpha Crucible Quant - Docker Deployment Script for Linux/Mac
# This script deploys the application using Docker containers

echo "Alpha Crucible Quant - Docker Deployment"
echo "======================================"
echo

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "Error: Docker is not running or not installed!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found in project root!"
    echo "Please copy .env_template to .env and configure your settings."
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "Building and starting Docker containers..."
echo

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start containers
echo "Building and starting new containers..."
docker-compose up --build -d

# Check if containers started successfully
sleep 10

echo
echo "Checking container status..."
docker-compose ps

echo
echo "Deployment completed!"
echo
echo "Your application is now running at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- Nginx Proxy: http://localhost:80"
echo
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo
