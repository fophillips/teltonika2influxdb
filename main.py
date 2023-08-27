import asyncio
import random
import sys
from os import environ as env

import aiomqtt
from influxdb_client import InfluxDBClient, WriteApi

MQTT_USER = env.get("MQTT_USER")
MQTT_PASS = env.get("MQTT_PASS")
MQTT_BROKER = env.get("MQTT_BROKER")
MQTT_CLIENT_ID = env.get(
    "MQTT_CLIENT_ID", f"teltonika2influxdb-{random.randint(0, 1000)}"
)

try:
    TELTONIKA_IP = env["TELTONIKA_IP"]
except KeyError:
    print("[ERROR] Teltonika IP must be given")
    sys.exit(1)

INFLUXDB_URL = env.get("INFLUXDB_URL", "http://localhost:8086")

try:
    INFLUXDB_API_TOKEN = env["INFLUXDB_API_TOKEN"]
except KeyError:
    print("[ERROR] InfluxDB API token must be provided")
    sys.exit(1)

try:
    INFLUXDB_ORG = env["INFLUXDB_ORG"]
except KeyError:
    print("[ERROR] InfluxDB API token must be provided")
    sys.exit(1)

FIELDS = ["temperature", "signal", "network", "connection", "uptime", "wan"]


async def read(client: aiomqtt.Client, idb_write: WriteApi):
    async with client.messages() as messages:
        await client.subscribe("teltonika/device/+/+")
        async for message in messages:
            write_to_influxdb(idb_write, message)


async def send_get(client: aiomqtt.Client):
    while True:
        for field in FIELDS:
            await client.publish("device/get", field)
        await asyncio.sleep(30)


def write_to_influxdb(idb_write: WriteApi, message: aiomqtt.Message):
    _, _, device_id, field = str(message.topic).split("/")
    try:
        value = int(message.payload)
        value = f"{value}i"
    except ValueError:
        value = message.payload.decode("utf-8")
        value = f'"{value}"'
    record = f"teltonika,device_id={device_id} {field}={value}"
    print(record)
    idb_write.write("teltonika", record=[record])


async def main():
    idb_client = InfluxDBClient(
        url=INFLUXDB_URL, token=INFLUXDB_API_TOKEN, org=INFLUXDB_ORG
    )
    idb_write = idb_client.write_api()
    async with aiomqtt.Client(
        MQTT_BROKER, username=MQTT_USER, password=MQTT_PASS, client_id=MQTT_CLIENT_ID
    ) as read_client:
        async with aiomqtt.Client(TELTONIKA_IP) as write_client:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(read(read_client, idb_write))
                tg.create_task(send_get(write_client))


asyncio.run(main())
