import time
import os
from collections import deque
from dotenv import load_dotenv

load_dotenv()

TREND_WINDOW = int(os.getenv("TREND_WINDOW"))
HDOP_BAD = float(os.getenv("HDOP_BAD"))
DEGRADE_TIME = float(os.getenv("DEGRADE_TIME"))
HDOP_RATIO_BAD = float(os.getenv("HDOP_RATIO_BAD"))

usb_hdop_history = deque(maxlen=TREND_WINDOW)
can_hdop_history = deque(maxlen=TREND_WINDOW)

bad_ratio_count = 0
degrade_start = None
last_degrade_alert = 0
last_ratio_alert = 0
last_trend_alert = 0

ALERT_COOLDOWN = 5


def check_precision(state):
    global bad_ratio_count
    global degrade_start
    global last_degrade_alert
    global last_ratio_alert
    global last_trend_alert

    alerts = []

    usb = state["usb"]["data"]
    can = state["can"]["data"]

    if not usb or not can:
        return alerts

    usb_hdop = usb.get("hdop")
    can_hdop = can.get("hdop")

    if usb_hdop is None or can_hdop is None:
        return alerts

    now = time.time()

    usb_hdop_history.append(usb_hdop)
    can_hdop_history.append(can_hdop)

# USB HDOP degradation

    if usb_hdop > HDOP_BAD:
        if degrade_start is None:
            degrade_start = now

        duration = now - degrade_start

        if duration > DEGRADE_TIME and now - last_degrade_alert > ALERT_COOLDOWN:
            alerts.append(
                f"USB precision degraded: HDOP: {usb_hdop:.2f} for {duration:.1f}s"
            )
            last_degrade_alert = now
    else:
        degrade_start = None

# USB vs CAN ratio

    ratio = usb_hdop / max(can_hdop, 0.1)

    if ratio > HDOP_RATIO_BAD:
        bad_ratio_count += 1
    else:
        bad_ratio_count = 0

    if bad_ratio_count >= 3 and now - last_ratio_alert > ALERT_COOLDOWN:
        alerts.append(
            f"USB HDOP significantly worse than CAN (ratio {ratio:.2f})"
        )
        last_ratio_alert = now
        bad_ratio_count = 0

# USB HDOP trend

    if len(usb_hdop_history) == TREND_WINDOW:
        first = usb_hdop_history[0]
        last = usb_hdop_history[-1]

        if first > 0 and last > first * 1.5 and now - last_trend_alert > ALERT_COOLDOWN:
            alerts.append(
                f"USB HDOP trend ({first:.2f} -> {last:.2f})"
            )
            last_trend_alert = now

    return alerts