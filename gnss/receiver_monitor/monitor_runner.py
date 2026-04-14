import time
import copy
from .receivers import state, state_lock
from tools.influx_writer import push_metrics, push_alerts
from .precision_monitoring import check_precision
from .sat_time_monitoring import check_signal
import os
from dotenv import load_dotenv

load_dotenv()

INFLUX_CHECK_INTERVAL= int(os.getenv("INFLUX_CHECK_INTERVAL"))



def run_monitor():
    while True:
        time.sleep(INFLUX_CHECK_INTERVAL)

        with state_lock:
            snapshot = copy.deepcopy(state)

        usb = snapshot["usb"]["data"]

        signal_alerts = check_signal(snapshot)
        precision_alerts = check_precision(snapshot)

        all_alerts = signal_alerts + precision_alerts

        if all_alerts:
            push_alerts(all_alerts, "usb")

            for alert in all_alerts:
                print("ALERT:", alert)

        else:
            if usb:
                print(
                    f"USB OK: sat={usb['satellites']}, "
                    f"fix={usb['fix']}, "
                    f"hdop={usb['hdop']}, "
                    f"time={usb['time']}"
                )

        push_metrics(snapshot, INFLUX_CHECK_INTERVAL)