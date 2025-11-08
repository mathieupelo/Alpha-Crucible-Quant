#!/bin/bash

echo "========================================"
echo "  Alpha Crucible Quant - Deploy Script"
echo "========================================"
echo

echo "[1/4] Stopping and removing existing containers..."
docker-compose down -v
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to stop containers"
    exit 1
fi

echo "[2/4] Removing existing images..."
docker-compose down --rmi all
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to remove some images (this is usually OK)"
fi

echo "[3/4] Building and starting fresh containers..."
docker-compose up --build -d
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build/start containers"
    exit 1
fi

echo "[4/4] Checking container status..."
sleep 5
docker-compose ps

echo
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
echo
echo "Your application is now running at:"
echo "  Frontend: http://localhost/"
echo "  API:      http://localhost:8000/api"
echo "  Health:   http://localhost:8000/health"
echo
echo "To view logs: docker-compose logs -f"
echo "To stop:     docker-compose down"
echo