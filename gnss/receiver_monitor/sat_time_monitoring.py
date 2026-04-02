import time
from helpers.gnss_parser import parse_gnss_time

# thresholds (can later move to config)
MIN_SATELLITES = 3
DEGRADED_DIFF = 8
TIMEOUT = 3
TIME_JUMP_THRESHOLD = 5

last_usb_time = None


def check_signal(state):
    global last_usb_time

    alerts = []

    usb = state["usb"]["data"]
    can = state["can"]["data"]
    now = time.time()

    #receiver timeout

    if state["usb"]["last_time"] and now - state["usb"]["last_time"] > TIMEOUT:
        alerts.append("USB receiver signal cutout")
        return alerts

    if not usb:
        return alerts

    #low satellite count

    if usb["satellites"] < MIN_SATELLITES:
        alerts.append("USB weak signal")

    #receiver comparison with satellite count

    if can and usb["satellites"] < can["satellites"] - DEGRADED_DIFF:
        alerts.append("USB significantly worse than CAN")

    #time anomaly detection

    usb_time_raw = usb.get("time")
    usb_time = parse_gnss_time(usb_time_raw)

    if usb_time is not None:

        if last_usb_time is not None:
            jump = abs(usb_time - last_usb_time)

            if jump > TIME_JUMP_THRESHOLD:
                alerts.append(f"USB GNSS time jump detected: {jump:.2f}s")

        last_usb_time = usb_time

    return alerts