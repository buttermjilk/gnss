from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os
from dotenv import load_dotenv

load_dotenv()

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG", "organization")
BUCKET = "gnss_monitor"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)


def push_metrics(state, interval):
    now = time.time()
    points = []

    for r in ["usb", "can"]:
        receiver = state[r]
        data = receiver["data"]

        if not data:
            continue

        msg_count = receiver["msg_count"]
        corrupt_count = receiver["corrupt_count"]

        corrupt_ratio = corrupt_count / max(msg_count, 1)

        point = (
            Point("gnss_receiver")
            .tag("receiver", r)
            .field("satellites", data["satellites"])
            .field("fix", data["fix"])
            .field("hdop", data["hdop"])
            .field("time", data["time"])
            .field("corrupt_ratio", corrupt_ratio)
            .time(int(now * 1e9))
        )

        points.append(point)

    if points:
        try:
            write_api.write(bucket=BUCKET, org=ORG, record=points)
        except Exception as e:
            print("Influx metrics write failed:", e)


def push_alerts(alerts, receiver="usb"):
    if not alerts:
        return

    now = time.time()
    points = []

    for i, alert in enumerate(alerts):
        point = (
            Point("gnss_alert")
            .tag("receiver", receiver)
            .tag("alert", alert)
            .field("value", 1)
            .time(int((now + i * 1e-6) * 1e9))
        )
        points.append(point)

    try:
        write_api.write(bucket=BUCKET, org=ORG, record=points)
    except Exception as e:
        print("Influx alerts write failed:", e)