import time
import os
from helpers.gnss_parser import parse_gnss_time
from helpers.haversine import haversine
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = float(os.getenv("TIMEOUT"))
DEGRADED_DIFF = float(os.getenv("DEGRADED_DIFF"))
MIN_SATELLITES = int(os.getenv("MIN_SATELLITES"))
POSITION_DIFF_THRESHOLD = float(os.getenv("POSITION_DIFF_THRESHOLD"))
MAX_SPEED = float(os.getenv("MAX_SPEED"))
TIME_DIFF_THRESHOLD = float(os.getenv("TIME_DIFF_THRESHOLD"))
SPOOF_SCORE_THRESHOLD = int(os.getenv("SPOOF_SCORE_THRESHOLD"))


def check_signal(state):
    alerts = []
    now = time.time()

    usb = state["usb"]["data"]
    can = state["can"]["data"]

    score = 0

# receiver timeout

    if state["usb"]["last_time"] and now - state["usb"]["last_time"] > TIMEOUT:
        alerts.append("USB receiver signal cutout")
        score += 2

    if not usb:
        return alerts


# satellite checks

    if usb.get("satellites", 0) < MIN_SATELLITES:
        alerts.append("USB weak signal")
        score += 1

    if can and usb.get("satellites") is not None and can.get("satellites") is not None:
        if usb["satellites"] < can["satellites"] - DEGRADED_DIFF:
            alerts.append("USB satellites significantly lower than CAN")
            score += 1


# fix quality degradation

    if usb.get("fix", 0) < 1:
        alerts.append("USB lost fix")
        score += 1


# position mismatch

    if can:
        if all(k in usb for k in ("lat", "lon")) and all(k in can for k in ("lat", "lon")):
            dist = haversine(usb["lat"], usb["lon"], can["lat"], can["lon"])

            if dist > POSITION_DIFF_THRESHOLD:
                alerts.append(f"Position mismatch USB vs CAN: {dist:.1f} m")
                score += 3

#impossible movement 

    prev = state["usb"].get("prev_position")

    if prev and all(k in usb for k in ("lat", "lon")):
        dist = haversine(prev["lat"], prev["lon"], usb["lat"], usb["lon"])
        dt = now - prev["time"]

        if dt > 0:
            speed = dist / dt

            if speed > MAX_SPEED:
                alerts.append(f"Impossible movement detected: {speed:.1f} m/s")
                score += 3


# store for next iteration

    if all(k in usb for k in ("lat", "lon")):
        state["usb"]["prev_position"] = {
            "lat": usb["lat"],
            "lon": usb["lon"],
            "time": now
        }


# time mismatch

    usb_time = parse_gnss_time(usb.get("time"))
    can_time = parse_gnss_time(can.get("time")) if can else None

    if usb_time and can_time:
        diff = abs(usb_time - can_time)

        if diff > TIME_DIFF_THRESHOLD:
            alerts.append(f"USB vs CAN time mismatch: {diff:.2f}s")
            score += 2


#GNSS time jump

    last_usb_time = state["usb"].get("last_gnss_time")

    if usb_time is not None:
        if last_usb_time is not None:
            jump = abs(usb_time - last_usb_time)

# compare against real elapsed time
            
            last_wall = state["usb"].get("last_wall_time")
            if last_wall:
                real_dt = now - last_wall

                if abs(jump - real_dt) > TIME_DIFF_THRESHOLD:
                    alerts.append(f"USB GNSS time anomaly: jump {jump:.2f}s")
                    score += 2

        state["usb"]["last_gnss_time"] = usb_time
        state["usb"]["last_wall_time"] = now


    if score >= SPOOF_SCORE_THRESHOLD:
        alerts.append(f"Possible spoofing detected (score={score})")

    return alerts