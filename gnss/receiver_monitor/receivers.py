import socket
import serial
import time
from .nmea_parser import parse_gga

#shared data state, message are compared to eachother from each source
state = {
    "usb": {"data": None, "last_time": None},
    "eth": {"data": None, "last_time": None}
}

#read ethernet port data
def read_eth():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 10110))
    file = sock.makefile()

    while True:
        line = file.readline()
        if not line:
            continue
        line = line.strip()
        data = parse_gga(line)
        if data:
            # update the shared state
            state["eth"]["data"] = data
            state["eth"]["last_time"] = time.time()
            # print for debugging
            print("ETH sat:", data["satellites"], "fix:", data["fix"])
            

#read usb port data
def read_usb():
    ser = serial.Serial("/dev/ttyUSB0", 4800, timeout=1)
    while True:
        line = ser.readline().decode(errors="ignore")
        if not line:
            continue
        line = line.strip()
        data = parse_gga(line)
        if data:
            # update the shared state
            state["usb"]["data"] = data
            state["usb"]["last_time"] = time.time()
            #print for debugging
            print("USB sat:", data["satellites"], "fix:", data["fix"])