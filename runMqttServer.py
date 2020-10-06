from SimConnect import *
import logging
from SimConnect.Enum import *
from time import sleep
import paho.mqtt.client as mqtt

"""Mqtt functions and settings"""
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/FS/SET/#")

def on_message(client, userdata, msg):
    LOGGER.debug(msg.topic + " " + str(msg.payload))
    if len(msg.topic.split("/")) < 5:
        LOGGER.error("invalid topic")
        return 0
    typ =  msg.topic.split("/")[3]
    dataPoint = msg.topic.split("/")[4]
    LOGGER.debug("TYP=" + typ + " Datapoint = " + dataPoint)
    payload = msg.payload.decode("utf-8")
    """Check dataPoint"""
    if typ == "LIGHT":
        dataset = ""
        for datasetName in toggle_lights:
            if dataPoint in datasetName:
                dataset = datasetName
                continue
        if dataset != "":
            light = ae.find(dataset)
            light()
    elif typ == "MIX":
        dataset = ""
        for datasetName in toggle_other:
            if dataPoint in datasetName:
                dataset = datasetName
                continue
        if dataset != "":
            other = ae.find(dataset)
            if payload == "":
                other()
    elif typ == "EVENT":
        event = ae.find(dataPoint)
        if payload == "":
            event()

def publishToMqttBroker(topic,value):
    if str(value) != "-999999" and str(value) != "-999,999":
        client.publish(topic,value)
        #LOGGER.debug(topic + " = " + str(value))

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

toggle_other = [
    'SMOKE_TOGGLE',
    'GEAR_TOGGLE',
    'PITOT_HEAT_TOGGLE',
    'PARKING_BRAKES',
]

toggle_lights = [
    'TOGGLE_TAXI_LIGHTS',
    'TOGGLE_BEACON_LIGHTS',
    'TOGGLE_WING_LIGHTS',
    'TOGGLE_NAV_LIGHTS',
    'TOGGLE_CABIN_LIGHTS',
    'LANDING_LIGHTS_TOGGLE',
    'PANEL_LIGHTS_TOGGLE',
    'ALL_LIGHTS_TOGGLE',
    'STROBES_TOGGLE',
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

"""Functions"""
def thousandify(x):
    return f"{x:,}"

def publishNavigationData():
    topic = "/FS/NAV/"
    publishToMqttBroker(topic+"LATITUDE",aq.get("PLANE_LATITUDE"))
    publishToMqttBroker(topic+"LONGITUDE",aq.get("PLANE_LONGITUDE"))
    publishToMqttBroker(topic+"MAGNETIC_COMPASS",aq.get("MAGNETIC_COMPASS"))
    publishToMqttBroker(topic+"MAGVAR",aq.get("MAGVAR"))
    publishToMqttBroker(topic+"VERTICAL_SPEED",aq.get("VERTICAL_SPEED"))
    publishToMqttBroker(topic+"PLANE_ALTITUDE",thousandify(round(aq.get("PLANE_ALTITUDE"))))

def publishAirspeedData():
    publishToMqttBroker("/FS/AIRSPEED",round(aq.get("AIRSPEED_INDICATED")))

def publishEngineData():
    topic = "/FS/ENG/"
    publishToMqttBroker(topic+"NUMBER_OF_ENGINES",str(round(aq.get("NUMBER_OF_ENGINES"))))
    publishToMqttBroker(topic+"GENERAL_ENG_RPM",round(aq.get("GENERAL_ENG_RPM:1")))
    publishToMqttBroker(topic+"AVL",round(aq.get("TURB_ENG_N1:1")))
    fuel_percentage = (aq.get("FUEL_TOTAL_QUANTITY") / aq.get("FUEL_TOTAL_CAPACITY")) * 100
    publishToMqttBroker(topic+"FUEL_PERCENTAGE",round(fuel_percentage))

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

if __name__ == '__main__':
    client.loop_start()
    while True:
        publishNavigationData()
        publishFlapsData()
        publishTrimData()
        #publishAutopilotData()
        publishEngineData()
        publishAirspeedData()
        publishLightsData()
        sleep(2)