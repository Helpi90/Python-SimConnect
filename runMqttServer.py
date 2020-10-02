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
request_lights = [
    'LIGHT_STROBE',
    'LIGHT_PANEL',
    'LIGHT_LANDING',
    'LIGHT_TAXI',
    'LIGHT_BEACON',
    'LIGHT_NAV',
    'LIGHT_WING'
]
request_autopilot = [
	'AUTOPILOT_MASTER',
	'AUTOPILOT_AVAILABLE',
	'AUTOPILOT_NAV_SELECTED',
	'AUTOPILOT_WING_LEVELER',
	'AUTOPILOT_NAV1_LOCK',
	'AUTOPILOT_HEADING_LOCK',
	'AUTOPILOT_HEADING_LOCK_DIR',
	'AUTOPILOT_ALTITUDE_LOCK',
	'AUTOPILOT_ALTITUDE_LOCK_VAR',
	'AUTOPILOT_ATTITUDE_HOLD',
	'AUTOPILOT_GLIDESLOPE_HOLD',
	'AUTOPILOT_PITCH_HOLD_REF',
	'AUTOPILOT_APPROACH_HOLD',
	'AUTOPILOT_BACKCOURSE_HOLD',
	'AUTOPILOT_VERTICAL_HOLD_VAR',
	'AUTOPILOT_PITCH_HOLD',
	'AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE',
	'AUTOPILOT_FLIGHT_DIRECTOR_PITCH',
	'AUTOPILOT_FLIGHT_DIRECTOR_BANK',
	'AUTOPILOT_AIRSPEED_HOLD',
	'AUTOPILOT_AIRSPEED_HOLD_VAR',
	'AUTOPILOT_MACH_HOLD',
	'AUTOPILOT_MACH_HOLD_VAR',
	'AUTOPILOT_YAW_DAMPER',
	'AUTOPILOT_RPM_HOLD_VAR',
	'AUTOPILOT_THROTTLE_ARM',
	'AUTOPILOT_TAKEOFF_POWER ACTIVE',
	'AUTOTHROTTLE_ACTIVE',
	'AUTOPILOT_VERTICAL_HOLD',
	'AUTOPILOT_RPM_HOLD',
	'AUTOPILOT_MAX_BANK',
	'FLY_BY_WIRE_ELAC_SWITCH',
	'FLY_BY_WIRE_FAC_SWITCH',
	'FLY_BY_WIRE_SEC_SWITCH',
	'FLY_BY_WIRE_ELAC_FAILED',
	'FLY_BY_WIRE_FAC_FAILED',
	'FLY_BY_WIRE_SEC_FAILED'
]

def thousandify(x):
    return f"{x:,}"

def getRPM():
    publishToMqttBroker("/FS/RPM", aq.get("GENERAL_ENG_RPM1"))

def publishNavigationData():
    topic = "/FS/NAV/"
    publishToMqttBroker(topic+"LATITUDE",aq.get("PLANE_LATITUDE"))
    publishToMqttBroker(topic+"LONGITUDE",aq.get("PLANE_LONGITUDE"))
    publishToMqttBroker(topic+"MAGNETIC_COMPASS",aq.get("MAGNETIC_COMPASS"))
    publishToMqttBroker(topic+"MAGVAR",aq.get("MAGVAR"))
    publishToMqttBroker(topic+"VERTICAL_SPEED",aq.get("VERTICAL_SPEED"))

def publishAirspeedData():
    publishToMqttBroker("/FS/AIRSPEED",round(aq.get("AIRSPEED_INDICATED")))

def publishEngineData():
    topic = "/FS/ENG/"
    publishToMqttBroker(topic+"NUMBER_OF_ENGINES",str(round(aq.get("NUMBER_OF_ENGINES"))))
    publishToMqttBroker(topic+"GENERAL_ENG_RPM",round(aq.get("GENERAL_ENG_RPM:1")))
    publishToMqttBroker("AVL",round(aq.get("TURB_ENG_N1:1")))
    fuel_percentage = (aq.get("FUEL_TOTAL_QUANTITY") / aq.get("FUEL_TOTAL_CAPACITY")) * 100
    publishToMqttBroker(topic+"FUEL_PERCENTAGE",round(fuel_percentage))
    #print(aq.get("ENGINE_TYPE"))
    #print(aq.get("TURB_ENG_N1:1"))

    #print(aq.get("TURB_ENG_N2:1"))

def publishFlapsData():
    topic = "/FS/FLAPS/"
    publishToMqttBroker(topic+"FLAPS_HANDLE_PERCENT",round(aq.get("FLAPS_HANDLE_PERCENT") * 100))

def publishTrimData():
    topic = "/FS/TRIM/"
    publishToMqttBroker(topic+"ELEVATOR_TRIM_PCT",round(aq.get("ELEVATOR_TRIM_PCT") * 100))
    publishToMqttBroker(topic+"RUDDER_TRIM_PCT",round(aq.get("RUDDER_TRIM_PCT") * 100))

def publishAutopilotData():
    topic = "/FS/AUTO"
    for dataPoint in request_autopilot:
        data = aq.get(dataPoint)
        publishToMqttBroker(topic+dataPoint,data)

def publishLightsData():
    topic = "/FS/LIGHTS/"
    for light in request_lights:
        state = aq.get(light)
        publishToMqttBroker(topic+light,state)

def setTaxiLight():
    taxiLight = ae.find("TOGGLE_TAXI_LIGHTS")
    taxiLight()


if __name__ == '__main__':
    while True:
        print("-------------------------------------\n")
        publishNavigationData()
        print("-------------------------------------\n")
        publishFlapsData()
        print("-------------------------------------\n")
        publishTrimData()
        print("-------------------------------------\n")
        #publishAutopilotData()
        print("-------------------------------------\n")
        publishEngineData()
        print("-------------------------------------\n")
        publishAirspeedData()
        print("-------------------------------------\n")
        publishLightsData()
        print("-------------------------------------\n")
        sleep(2)
    sm.exit()