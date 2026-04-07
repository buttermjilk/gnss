#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "stopping monitoring service..."
pkill -f receiver_monitor/main.py 2>/dev/null || true

sleep 2

echo "monitoring service stopped"



echo "stopping docker containers..."
sudo docker compose down

sleep 4

echo "docker containers stopped"

echo "deactivating venv"
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

echo "venv deactivated"



echo "bringing CAN interfaces down"

sudo ip link set can0 down 2>/dev/null || true
sudo ip link set can1 down 2>/dev/null || true

sleep 2

echo "CAN interfaces down"



echo "freeing USB0 port"

sudo fuser -k /dev/ttyUSB0 2>/dev/null || true

sleep 2

echo "USB0 port freed"



echo "system stopped successfully"