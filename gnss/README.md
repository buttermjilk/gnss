![Flowchart](flowchart.jpg)

Orchestrator: Creates 2 extra threads, assigns them to read 1 source of GNSS data per thread. Uses main thread to run monitor loop. 

Receivers: Uses libraries and a custom function to read and parse GNSS data and all its fields from USB and ETH source. Also uses a shared state sort of system, which syncs / matches the messages, so in comparison there is always the most recent ETH message for the most recent USB message. 


Monitoring_runner: 

A loop which is the core of the program. It takes in messages from the receivers and runs them through sat-time monitoring and precision monitoring functions. And then calls the influx writer to push the metrics. 


Sat-time_monitoring: 

Uses a function with if- clauses to check for things like time jumps, satellite amount, signal timeout etc. This gets ran every message. 

 
Precision_monitoring: 

Uses a function with if- clauses to monitor HDOP metrics. Check for things like straight up HDOP degradation or degradation trends (hdop worsening bit by bit over time). 

 
Influx_writer: 

A pretty run of the mill program that writes all of our metrics to influxDB. 

 
Grafana dashboard: 

This pulls from our influxDB bucket and displays all the wanted info on a realtime dashboard. 

All of the microservices run in docker containers! 