import socket
import serial

from .nmea_parser import parse_gga

#reads output of ETH port
def read_eth():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 10110))
    file = sock.makefile()

    while True:
        line = file.readline().strip()
        if line:
            data = parse_gga(line)
            if data:
                    print("sat:", data["satellites"], "fix:", data["fix"])
                    print("ETH:", line)

        