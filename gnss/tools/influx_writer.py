from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG", "organization")
BUCKET = "gnss_monitor"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def push_metrics(state, interval=3):
    now = time.time()
    points = []

    for r in ["usb", "eth"]:
        receiver = state[r]
        data = receiver["data"]

        if not data:
            continue

        msg_count = receiver["msg_count"]
        corrupt_count = receiver["corrupt_count"]

        msg_rate = msg_count / interval
        corrupt_ratio = corrupt_count / max(msg_count, 1)

        point = (
            Point("gnss_receiver")
            .tag("receiver", r)
            .field("satellites", data["satellites"])
            .field("fix", data["fix"])
            .field("hdop", data["hdop"])
            .field("time", data["time"])
            .field("message_rate", msg_rate)
            .field("corrupt_ratio", corrupt_ratio)
            .time(int(now * 1e9))
        )

        points.append(point)

        receiver["msg_count"] = 0
        receiver["corrupt_count"] = 0

    if points:
        write_api.write(bucket=BUCKET, org=ORG, record=points)