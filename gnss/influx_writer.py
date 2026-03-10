from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os

INFLUX_URL =  os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-token")
ORG = os.getenv("INFLUX_ORG", "my-org")
BUCKET = os.getenv("INFLUX_BUCKET", "my-bucket")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def push_metrics(state):
    now = time.time()
    for r in ["usb", "eth"]:
        receiver = state[r]
        data = receiver["data"]
        if not data:
            continue

        msg_rate = receiver["msg_count"] / 3  # assuming CHECK_INTERVAL=3
        corrupt_ratio = receiver["corrupt_count"] / max(receiver["msg_count"], 1)

        point = (
            Point(r)
            .tag("receiver", r)
            .field("satellites", data["satellites"])
            .field("fix", data["fix"])
            .field("message_rate", msg_rate)
            .field("corrupt_ratio", corrupt_ratio)
            .time(int(now * 1e9))  # nanoseconds
        )

        write_api.write(bucket=BUCKET, org=ORG, record=point)

        # reset counters for next interval
        receiver["msg_count"] = 0
        receiver["corrupt_count"] = 0