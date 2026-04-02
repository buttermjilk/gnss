#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "freeing up USB0 port"
sudo fuser -k /dev/ttyUSB0 2>/dev/null || true

sleep 2

echo "USB0 port freed"



echo "setting up can interface"

sudo ip link set can0 up type can bitrate 250000
sudo ip link set can1 up type can bitrate 250000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536

sleep 2

echo "can interface set up, receiver should output data"



echo "starting docker containers"

sudo docker compose up -d

sleep 4

echo "docker containers started"



echo "starting monitoring service"

python3 -m receiver_monitor.main

sleep 2

echo "service started"



echo "system started succesfully"