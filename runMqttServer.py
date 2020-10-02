from SimConnect import *
import logging
from SimConnect.Enum import *
from time import sleep
import paho.mqtt.client as mqtt

"""Mqtt functions and settings"""
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def publishToMqttBroker(topic,value):
    if str(value) != "-999999":
        client.publish(topic,value)
        LOGGER.info(topic + " = " + str(value))

def publishDatasetToMqttBroker(datasetName):
    dataset = request_trim
    for datapoint in dataset:
        data = aq.get(datapoint)
        if str(data) != "-999999":
            client.publish("/FS/"+datasetName.split("_")[1]+"/"+datapoint,data)
            LOGGER.info("/FS/"+datasetName.split("_")[1]+"/"+datapoint + " = " + str(data))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.89.52", 1883, 60)
client.publish("/FS/CONNECTION", "CONNECTED")

"""Logging settings"""
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.info("START")

"""Simconnect Settings"""
# creat simconnection and pass used user classes
sm = SimConnect()
aq = AircraftRequests(sm)
ae = AircraftEvents(sm)

"""Datasets"""
request_trim = [
	'ROTOR_LATERAL_TRIM_PCT',  # Trim percent
	'ELEVATOR_TRIM_POSITION',  # Elevator trim deflection
	'ELEVATOR_TRIM_INDICATOR',
	'ELEVATOR_TRIM_PCT',  # Percent elevator trim
	'AILERON_TRIM',  # Angle deflection
	'AILERON_TRIM_PCT',  # The trim position of the ailerons. Zero is fully retracted.
	'RUDDER_TRIM_PCT',  # The trim position of the rudder. Zero is no trim.
	'RUDDER_TRIM',  # Angle deflection
]

def thousandify(x):
    return f"{x:,}"

if __name__ == '__main__':
    while True:
        #client.publish("/FS/SPEED", round(aq.get("AIRSPEED_INDICATED")))
        publishToMqttBroker("/FS/AIRSPEED",round(aq.get("AIRSPEED_INDICATED")))
        #print(round(aq.get("AIRSPEED_INDICATED")))
        publishToMqttBroker("/FS/ALTITUDE",thousandify(round(aq.get("PLANE_ALTITUDE"))))
        print("-------------------------------------\n")
        sleep(1)
        publishDatasetToMqttBroker("request_trim")
        sleep(2)