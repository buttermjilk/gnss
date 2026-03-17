import socket
import serial
import time
from helpers.nmea_parser import parse_gga

# shared state, this synchronizes messages from each source
state = {
    "usb": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    },
    "eth": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    }
}

# read ethernet port data
def read_eth():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.128.209", 10110))
    file = sock.makefile()

    while True:
        line = file.readline()
        if not line:
            continue
        line = line.strip()

        state["eth"]["msg_count"] += 1

        if not line.startswith("$"):
            state["eth"]["corrupt_count"] += 1
            continue

        data = parse_gga(line)
        if data:
            state["eth"]["data"] = data
            state["eth"]["last_time"] = time.time()
            print("ETH sat:", data["satellites"], "fix:", data["fix"], "hdop:", data['hdop'], "time:", data['time'])


# read usb port data
def read_usb():
    ser = serial.Serial("/dev/ttyUSB0", 4800, timeout=1)
    while True:
        line = ser.readline().decode(errors="ignore")
        if not line:
            continue
        line = line.strip()

        state["usb"]["msg_count"] += 1

        if not line.startswith("$"):
            state["usb"]["corrupt_count"] += 1
            continue

        data = parse_gga(line)
        if data:
            state["usb"]["data"] = data
            state["usb"]["last_time"] = time.time()
            print("USB sat:", data["satellites"], "fix:", data["fix"], "hdop:", data['hdop'], "time:", data['time'])