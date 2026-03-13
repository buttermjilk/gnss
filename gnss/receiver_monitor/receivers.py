import socket
import serial
import time
from helpers.nmea_parser import parse_gga

# shared state, this synchronizes messages from each source
state = {
    "usb": {
        "data": None,          # last parsed data
        "last_time": None,     # last message timestamp
        "msg_count": 0,        # messages received
        "corrupt_count": 0     # messages that are corrupted / incomplete
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

        if line.startswith("$GP"):
            data = parse_gga(line)
            if data:

                # update state
                state["eth"]["data"] = data
                state["eth"]["last_time"] = time.time()
                state["eth"]["msg_count"] += 1
                print("ETH sat:", data["satellites"], "fix:", data["fix"], "hdop:", data['hdop'], "time:", data['time'])
            else:
                state["eth"]["corrupt_count"] += 1
        else:
            state["eth"]["corrupt_count"] += 1

# read usb port data
def read_usb():
    ser = serial.Serial("/dev/ttyUSB0", 4800, timeout=1)
    while True:
        line = ser.readline().decode(errors="ignore")
        if not line:
            continue
        line = line.strip()

        if line.startswith("$GP"):
            data = parse_gga(line)
            if data:

                # update state
                state["usb"]["data"] = data
                state["usb"]["last_time"] = time.time()
                state["usb"]["msg_count"] += 1
                print("USB sat:", data["satellites"], "fix:", data["fix"], "hdop:", data['hdop'], "time:", data['time'])
            else:
                state["usb"]["corrupt_count"] += 1
        else:
            state["usb"]["corrupt_count"] += 1