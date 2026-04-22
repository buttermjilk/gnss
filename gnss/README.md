This project reads GNSS data from two sources. One from a simple USB port broadcasting NMEA0183 data, and one straight from the CAN-bus broadcasting NMEA2000 encrypted data using a Rasberry Pi with a PICAN -M NMEA2000 HAT.

The premise is that the more low-grade receiver shows signs of jamming and signal quality degradation before the main one, giving the user more time to switch to other marine navigation approaches.

The data from the USB port gets used as is with minimal processing, where the data from the CAN bus is decoded with self-built decoders prioritizing latency and not needing to rely on third party providers.
The messages are then matched through a synced state cache and ran through different scripts containing anomaly detection logic.
The data along with the possible detected alerts gets written to InfluxDB and then displayed on real-time Grafana dashboards.

![Flowchart](flowchart.jpg)

Physical system components:

Raspberry Pi + CAN bus reader & NMEA 2000 HAT 

Raymarine RS150 + barebones USB GNSS receiver (Model unknown) 

12V / 7.0Ah Battery for powering the system 

[ Additional components include custom wiring, NMEA2000 splitter + other miscellaoneus parts ]
