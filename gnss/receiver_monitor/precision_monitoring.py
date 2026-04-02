import time
from collections import deque


#ultimately these would probably be read from a config file
HDOP_BAD = 3.0
HDOP_RATIO_BAD = 2.0
TREND_WINDOW = 5
DEGRADE_TIME = 9  # this is seconds)

usb_hdop_history = deque(maxlen=TREND_WINDOW)
can_hdop_history = deque(maxlen=TREND_WINDOW)

bad_ratio_count = 0
degrade_start = None


def check_precision(state):
    global bad_ratio_count
    global degrade_start

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

# USB HDOP signal degr

    if usb_hdop > HDOP_BAD:

        if degrade_start is None:
            degrade_start = now

        duration = now - degrade_start

        if duration > DEGRADE_TIME:
            alerts.append(
                f"USB precision degraded: HDOP {usb_hdop:.2f} for {duration:.1f}s"
            )
    else:
        degrade_start = None

# USB HDOP signal ratio

    ratio = usb_hdop / max(can_hdop, 0.1)

    if ratio > HDOP_RATIO_BAD:
        bad_ratio_count += 1
    else:
        bad_ratio_count = 0

    if bad_ratio_count >= 3:
        alerts.append(
            f"USB HDOP significantly worse than CAN (ratio {ratio:.2f})"
        )
        bad_ratio_count = 0

# USB HDOP trend worsening

    if len(usb_hdop_history) == TREND_WINDOW:

        first = usb_hdop_history[0]
        last = usb_hdop_history[-1]

        if last > first * 2:
            alerts.append(
                f"USB HDOP trend worsening ({first:.2f} -> {last:.2f})"
            )

    return alerts