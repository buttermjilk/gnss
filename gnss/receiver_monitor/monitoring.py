import time
from .receivers import state

#ultimately these would probably be read form a config file
CHECK_INTERVAL = 3
MIN_SATELLITES = 6
DEGRADED_DIFF = 5 #this is just satellite difference [ETH_Receiver - USB_Receiver]

def run_monitor():
    while True:
        time.sleep(CHECK_INTERVAL)
        usb = state["usb"]["data"]
        eth = state["eth"]["data"]
        now = time.time()

        if not usb:
            print("No USB data yet")
            continue

        if state["usb"]["last_time"] and now - state["usb"]["last_time"] > CHECK_INTERVAL:
            print("ALERT: USB receiver signal cutout")
        elif usb["satellites"] < MIN_SATELLITES:
            print("ALERT: USB weak signal")
        elif eth and usb["satellites"] < eth["satellites"] - DEGRADED_DIFF:
            print("ALERT: USB significantly worse than Ethernet")
        else:
            print(f"USB OK: sat={usb['satellites']}, fix={usb['fix']}")