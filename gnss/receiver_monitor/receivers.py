import socket
import serial
import time
import subprocess
import json
import can
import threading
from queue import Queue
import struct

from helpers.nmea_parser import parse_gga
from helpers.nmea2000_translator import checksum, dd_to_nmea


# shared state, this synchronizes messages from each source
state = {
    "usb": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    },
    "can": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    }
}

# read usb port data
import socket
import serial
import time
import subprocess
import json
import can
import threading
from queue import Queue
import struct

from helpers.nmea_parser import parse_gga
from helpers.nmea2000_translator import checksum, dd_to_nmea


# shared state, this synchronizes messages from each source
state = {
    "usb": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    },
    "can": {
        "data": None,
        "last_time": None,
        "msg_count": 0,
        "corrupt_count": 0
    }
}

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




# read and translate nmea2000 from can bus
def read_can():

    bus = can.Bus(channel="can0", bustype="socketcan", bitrate=250000)

    fast_packets = {}
    
    lat = None
    lon = None
    hdop = 1.0
    sats = 0
    fix = 2

    last_pass = 0

    while True:

        msg = bus.recv()

        can_id = msg.arbitration_id
        pgn = (can_id >> 8) & 0x1FFFF
        data = msg.data

# handling fast packets (satellite data)

        if pgn in (129029, 129540):

            frame = data[0] & 0x1F
            seq = data[0] >> 5
            key = (pgn, seq)

            if frame == 0:
                length = data[1]
                fast_packets[key] = {
                    "length": length,
                    "data": bytearray(data[2:])
                }
                continue

            if key not in fast_packets:
                continue

            fast_packets[key]["data"] += data[1:]

            pkt = fast_packets[key]

            if len(pkt["data"]) < pkt["length"]:
                continue

            payload = pkt["data"][:pkt["length"]]
            del fast_packets[key]

            # PGN 129029 - satellite and fix
            if pgn == 129029:

                if len(payload) > 34:
                    sats = payload[33]
                    fix = payload[31] & 0x0F


        # lat + long
        elif pgn == 129025:

            lat = struct.unpack("<i",data[0:4])[0]*1e-7
            lon = struct.unpack("<i",data[4:8])[0]*1e-7

        # hdop
        elif pgn == 129539:

            hdop = struct.unpack("<H",data[2:4])[0]*0.01



        # create nmea0183 block, print it and pass it forwards.

        now = time.time()

        if lat and lon and now-last_pass>=1:

            lat_s,lat_h = dd_to_nmea(lat,"lat")
            lon_s,lon_h = dd_to_nmea(lon,"lon")

            utc = time.strftime("%H%M%S.000",time.gmtime())

  
            # GGA
            gga_body = f"GPGGA,{utc},{lat_s},{lat_h},{lon_s},{lon_h},{fix},{sats:02d},{hdop:.2f},,M,,M,,"
            gga_sentence = f"${gga_body}*{checksum(gga_body)}"


            # parse exactly like USB
            data = parse_gga(gga_sentence)
            if data:
                state["can"]["data"] = data
                state["can"]["last_time"] = time.time()
                state["can"]["msg_count"] += 1

                print(
                    "CAN sat:",
                    data["satellites"],
                    "fix:",
                    data["fix"],
                    "hdop:",
                    data["hdop"],
                    "time:",
                    data["time"]
                )

            else:
                state["can"]["corrupt_count"] += 1

            last_pass = now
