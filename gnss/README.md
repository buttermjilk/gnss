This project reads GNSS data from two sources. One from a simple USB port broadcasting NMEA0183 data, and one straight from the CAN-bus broadcasting NMEA2000 encrypted data using a Rasberry Pi with a PICAN -M NMEA2000 HAT.

The data from the USB port gets used as is with minimal processing, where the data from the CAN bus is decoded with self-built decoders prioritizing latency and not needing to rely on third party providers.
The messages are then matched through a synced state cache and run through different scripts containing anomaly detection logic.
The data along with the possible alerts created gets written to InfluxDB and then displayed on a real-time Grafana dashboard.

![Flowchart](flowchart.jpg)
