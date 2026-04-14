![Flowchart](flowchart.jpg)

Orchestrator: Creates 2 extra threads, assigns them to read 1 source of GNSS data per thread. Uses main thread to run monitor loop. 

Receivers: Uses libraries to read data straight from our USB receiver. For the other receiver we are tapping straight into the CAN-Bus and manually decoding packets and harvesting wanted information. This information gets reconstructed to NMEA0183 messages from the NMEA2000 data.


Monitoring_runner: 

A loop which is the core of the program. It takes in messages from the receivers and runs them through sat-time monitoring and precision monitoring functions. And then calls the influx writer to push the metrics. 


Sat-time_monitoring: 

A detection script that monitors and classifies issues, checking for problems like time jumps, impossible movement, satellite amount, signal timeout etc.

 
Precision_monitoring: 

A detection script that monitors and classifies issues with HDOP. Check for things like straight up HDOP degradation or degradation trends.

Helper_scripts:

A collection of scripts related to parsing GGA messages, reconstructing NMEA0183 and decoding NMEA2000 messages.

 
Influx_writer: 

A pretty run of the mill program that writes all of our metrics to influxDB. 

 
Grafana dashboard: 

This pulls from our influxDB bucket and displays all the wanted info on a realtime dashboard. 

All of the microservices run in docker containers! 