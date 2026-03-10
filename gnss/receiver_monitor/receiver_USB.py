import socket
import serial

from .nmea_parser import parse_gga

#reads output of USB port
def read_usb():
    ser = serial.Serial("/dev/ttyUSB0", 4800, timeout=1)
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            data = parse_gga(line)
            if data:
                    print("sat:", data["satellites"], "fix:", data["fix"])
                    print("ETH:", line)