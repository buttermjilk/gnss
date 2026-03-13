import time
from .receivers import state
from influx_writer import push_metrics
from .precision_monitoring import check_precision
from .sat_time_monitoring import check_signal

CHECK_INTERVAL = 3


def run_monitor():
    while True:
        time.sleep(CHECK_INTERVAL)

        usb = state["usb"]["data"]

        # signal monitoring
        signal_alerts = check_signal(state)

        if signal_alerts:
            for alert in signal_alerts:
                print("ALERT:", alert)

        else:
            if usb:
                print(f"USB OK: sat={usb['satellites']}, fix={usb['fix']}, hdop={usb['hdop']}, time={usb['time']}")

        # precision monitoring
        precision_alerts = check_precision(state)

        for alert in precision_alerts:
            print("PRECISION ALERT:", alert)

        push_metrics(state, CHECK_INTERVAL)