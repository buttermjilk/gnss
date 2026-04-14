import sys
import json
import datetime

lat = None
lon = None
hdop = None
date = None
time = None

def checksum(s):
    cs = 0
    for c in s:
        cs ^= ord(c)
    return f"{cs:02X}"

def dd_to_nmea(val, latlon):
    deg = int(abs(val))
    minutes = (abs(val) - deg) * 60
    if latlon == "lat":
        hemi = "N" if val >= 0 else "S"
        return f"{deg:02d}{minutes:06.3f}", hemi
    else:
        hemi = "E" if val >= 0 else "W"
        return f"{deg:03d}{minutes:06.3f}", hemi

if __name__ == "__main__":
    for line in sys.stdin:
        msg = json.loads(line)

        if "pgn" not in msg:
            continue

        pgn = msg["pgn"]
        fields = msg["fields"]

        if pgn == 129025:
            lat = fields["Latitude"]
            lon = fields["Longitude"]

        elif pgn == 129539:
            hdop = fields["HDOP"]

        elif pgn == 129033:
            date = fields["Date"]
            time = fields["Time"]

        if lat and lon is not None:
            lat_str, lat_h = dd_to_nmea(lat, "lat")
            lon_str, lon_h = dd_to_nmea(lon, "lon")

            body = f"GPRMC,,A,{lat_str},{lat_h},{lon_str},{lon_h},,"
            print(f"${body}*{checksum(body)}")