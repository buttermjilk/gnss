import time
from .receivers import state
from tools.influx_writer import push_metrics, push_alerts
from .precision_monitoring import check_precision
from .sat_time_monitoring import check_signal

CHECK_INTERVAL = 3


def run_monitor():
    while True:
        time.sleep(CHECK_INTERVAL)

        usb = state["usb"]["data"]

        signal_alerts = check_signal(state)
        precision_alerts = check_precision(state)

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

        push_metrics(state, CHECK_INTERVAL)