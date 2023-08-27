# `teltonika2influxdb`

I created this utility to publish metrics from [Teltonika gateways](https://wiki.teltonika-networks.com/view/Monitoring_via_MQTT) to InfluxDB v2 because the gateway required `get` commands to be sent to retrieve metrics.

## How to use

Configuration is done through environment variables:

```
MQTT_USER=
MQTT_PASS=
MQTT_BROKER=
MQTT_TOPIC=
TELTONIKA_IP=
INFLUXDB_API_TOKEN=
INFLUXDB_URL=
INFLUXDB_ORG=
```