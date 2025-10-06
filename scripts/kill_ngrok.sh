#!/bin/bash
# Kill all Ngrok processes

echo "Killing all Ngrok processes..."
echo

# Stop all Ngrok processes
pkill -f ngrok >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Ngrok processes killed successfully."
else
    echo "No Ngrok processes were running."
fi

echo
echo "All Ngrok tunnels have been stopped."
echo "You can now run ./scripts/start_ngrok.sh to start a fresh tunnel."
echo
