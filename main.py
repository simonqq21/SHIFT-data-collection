'''
MQTT data packet format
{
    'datetime': (datetime object parsed into string),
    'expt_num': (integer),
    'sitename': (string),
    'type': (string eg. "temperature", "humidity", "light_intensity", "soil_moisture",  
            solution_pH", "solution_EC", "camera"),
    'index': (integer),
    'value': (float),
}
'''
import os
from time import sleep 
from datetime import datetime, date, time, timedelta
from hardware.growlights_camera import LightsCamera
from hardware.irrigation_pumps import SyncedPumps
from hardware.onewire_temperature_humidity import DHT22
from hardware.i2c_lightintensity import BH1750, TCA9548A
from hardware.analog_soilmoisture_ph_ec import ADS1115, SoilMoistureSensor, PH4502C, TDSMeter
import pandas as pd 
import paho.mqtt.client as mqtt
try:
    from hardware.pi_interfaces import onewires, i2c
except:
    print("main.py not running on RPi")

# MQTT broker 
mqttIP = "ccscloud2.dlsu.edu.ph"
mqttPort = 20010
clientname = "DLSU_SHIFT"
# MQTT data constants
expt_num = 0 
sitename = "DLSU-BLAST"
# MQTT topics 
main_topic = "sensor/dlsu/node-1/"
suffix_temperature = "temperature"
suffix_humidity = "humidity"
suffix_lightintensity = "light_intensity"
suffix_soilmoisture = "soil_moisture"
suffix_pH = "solution_pH"
suffix_EC = "solution_EC"
suffix_camera = "camera"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic)

def on_publish(client, username, mid):
    print("Message published")

def processDataForPublish(datetime, type, index, rawsensordata):
    global expt_num, sitename
    data = {
        'datetime': datetime,
        'expt_num': expt_num,
        'sitename': sitename,
        'type': type,
        'index': index,
        'value': rawsensordata,
    }
    return data

# mqtt client init
client = mqtt.Client(clientname)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
try:
    client.connect(mqttIP, mqttPort)
    print(client)
    client.loop_start()
except:
    print("Failed to connect to broker!")

if __name__ == "__main__":
    print(os.getcwd())
    # initialize onewire DHT22 temperature and humidity sensors 


    # initialize TCA9548A i2c multiplexer and i2c BH1750 light intensity sensors 

    # initialize ADS1115 i2c ADCs and analog channels for soil moisture sensors, PH4502C pH sensor, and TDS meter EC sensor 

    # initialize grow lights and camera with camera light
    lightscamera = LightsCamera(18, 27, 9, os.getcwd()+"/growlight_interval.json", os.getcwd()+"/camera_interval.json")
    # initialize irrigation pumps
    pumps = SyncedPumps((22, 23, 24), 10, os.getcwd()+"/pumps_interval.json")
    
    # datetimenow = datetime.combine(date.today(), time(hour=21, minute=0, second=0))
    datetimenow = datetime.now()
    checkingInterval = timedelta(seconds=10)
    sensorPollingInterval = timedelta(minutes=1) # 30 minutes
    lastUpdatedDate = date(year=1970, month=1, day=1)
    intervalLastChecked = datetime(year=1970, month=1, day=1)
    sensorsLastPolled = datetime(year=1970, month=1, day=1)
    
    while True:
        datetimenow += timedelta(seconds=1) 
        # datetimenow = datetime.now()
        # update the growLightIntervals and cameraIntervals with the times of the day 
        if (date.today() > lastUpdatedDate):
            datetimenow = datetime.now()
            lastUpdatedDate = date.today() 
            lightscamera.getGrowLightIntervalsPerDay()
            lightscamera.getCameraIntervalsPerDay()
            
        # loop to check the camera, growlights, and pump
        if (datetime.now() - intervalLastChecked >= checkingInterval):
            intervalLastChecked = datetime.now()
            # loop to check switch grow lights
            lightscamera.pollGrowLights(datetimenow)
            print("val={}".format(lightscamera.growlightval))
            '''
            while the camera is capturing an image, the growlight code must be overriden.
            '''
            # loop to capture image 
            lightscamera.pollCamera(datetimenow)
            if (lightscamera.newImage):
                # publish the image on MQTT
                print("binary image received")
                # print("binary image = {}".format(lightscamera.binaryImage)) 

                lightscamera.newImage = 0

            # loop to check and run irrigation pumps
            pumps.pollPumps(datetimenow)

        # loop to gather sensor data from all sensors, package it into json, and send it via MQTT 
        if (datetime.now() - sensorsLastPolled >= sensorPollingInterval):
            # temperature and humidity from DHT22 
            pass
            # light intensity from BH1750 

            # soil moisture, pH, and EC from soil moisture sensors. PH-4502C, and TDS Meter 1.0 

        
        sleep(1)