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
try:
    import os
    from time import sleep 
    import json 
    from datetime import datetime, date, time, timedelta
    from hardware.growlights_camera import LightsCamera
    from hardware.irrigation_pumps import SyncedPumps
    from hardware.onewire_temperature_humidity import DHT22
    from hardware.i2c_lightintensity import BH1750, TCA9548A
    from hardware.analog_soilmoisture_ph_ec import ADS1115, SoilMoistureSensor, PH4502C, TDSMeter
    import pandas as pd 
    import numpy as np
    import paho.mqtt.client as mqtt
except Exception as e:
    print(e)
try:
    from hardware.pi_interfaces import onewires, i2c
except:
    print("main.py not running on RPi")
from config import *

# create directories for collected data 
os.makedirs(csv_filepath, exist_ok=True)
os.makedirs(images_filepath, exist_ok=True)

# create csv file for sensor data if it doesnt exist 
df = pd.DataFrame.from_dict(sensor_data, orient='columns')
mode = 'w'
index=False
header=True
if os.path.exists(csv_filepath + csv_filename):
    mode = 'a'
    header=False
    print('exists!')
df.to_csv(csv_filepath + csv_filename, mode=mode, index=index, header=header)
columns = df.columns.values
print(columns)
# columns for image dataframe
camera_columns = np.array(list(image_data.keys()))
print(camera_columns)

# callback functions for MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic)

def on_publish(client, username, mid):
    print("Message published")

'''
return a dataframe containing the indexed sensor data to be transmitted
'''
def processSensorDataForPublishing(datetime, type, index, rawsensordata):
    global debug
    global expt_num, sitename
    data = sensor_data
    data["datetime"] = [datetime]
    data["expt_num"] = [expt_num]
    data["sitename"]= [sitename]
    data["type"]= [type]
    data["index"]= [index]
    data["value"]= [rawsensordata]
    df = pd.DataFrame(data, columns=columns)
    if debug:
        print(df)
    return df 

'''
save the sensor data dataframe to the local CSV file and transmit the sensor data 
dataframe to the MQTT main_topic
'''
def saveAndPublishData(df, sensorPublishTopic):
    print(df)
    df.to_csv(csv_filepath + csv_filename, mode='a', index=False, header=False)
    try:
        client.publish(sensorPublishTopic, df.to_json())
    except:
        print("Publish failed, check broker")

'''
return a dataframe containing the image data and metadata to be transmitted
'''
def processImageDataForPublishing(type, index, filename, binaryImage):
    global debug
    global expt_num, sitename
    data = image_data
    data["expt_num"] = [expt_num]
    data["sitename"]= [sitename]
    data["type"]= [type]
    data["index"]= [index]
    data["filename"]= [filename]
    data["imagedata"]= [binaryImage]
    df = pd.DataFrame(data, columns=camera_columns)
    if debug:
        print(df)
    return df 

'''
publish the captured image dataframe to the MQTT broker
'''
def publishImage(df, sensorPublishTopic):
    try:
        client.publish(sensorPublishTopic, df.to_json())
    except:
        print("Publish failed, check broker")

# mqtt client init
client = mqtt.Client(clientname)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
try:
    client.connect(mqttIP, mqttPort)
    print(client)
    client.loop_start()
except Exception as e:
    print("Failed to connect to broker!")
    print(e)

if __name__ == "__main__":
    print(program_root)
    # initialize onewire DHT22 temperature and humidity sensors 
    dhts = []
    for wire in onewires:
        dhts.append(DHT22(wire))

    # initialize TCA9548A i2c multiplexer and i2c BH1750 light intensity sensors 
    bhcount = 9 
    tca = TCA9548A(i2c)
    for si in range(bhcount):
        try:
            tca.addBH1750(si)
        except Exception as e:
            print(e)
            print("not running on Pi or device not connected properly") 

    # initialize ADS1115 i2c ADCs and analog channels for soil moisture sensors, PH4502C pH sensor, and TDS meter EC sensor 
    adss = []
    adss.append(ADS1115(i2c, addressIndex=0)) # soil moisture sensors 0-3
    adss.append(ADS1115(i2c, addressIndex=1)) # soil moisture sensors 4-7
    adss.append(ADS1115(i2c, addressIndex=2)) # soil moisture sensor 8, pH sensor, and EC sensor
    # add 9 soil moisture sensors throughout three ADS1115 consecutively from channel 0 of ADS1115 index 0
    adss[0].addSoilMoistureSensor(m=-0.505, b=3.92)
    adss[0].addSoilMoistureSensor(m=-1.33, b=3.88)
    adss[0].addSoilMoistureSensor(m=-0.993, b=3.89)
    adss[0].addSoilMoistureSensor(m=-0.532, b=4.05)
    adss[1].addSoilMoistureSensor(m=-0.47, b=4.12)
    adss[1].addSoilMoistureSensor(m=-0.456, b=4.12)
    adss[1].addSoilMoistureSensor(m=-0.402, b=4.11)
    adss[1].addSoilMoistureSensor(m=-0.488, b=4.11)
    adss[2].addSoilMoistureSensor(m=-0.993, b=3.89)
    # add 1 pH sensor to channel 1 of ADS1115 index 2
    adss[2].addPH4502C(m=-0.1723776224, b=3.77251049)
    # add 1 EC sensor 
    adss[2].addTDSMeter()

    # initialize grow lights and camera with camera light
    lightscamera = LightsCamera(growLightPin, cameraLightPin, cameraButtonPin, program_root+"/growlight_interval.json", program_root+"/camera_interval.json", images_filepath, images_filename_format)
    # initialize irrigation pumps
    pumps = SyncedPumps(pumpPins, pumpButtonPin, program_root+"/pumps_interval.json")
    
    while True:
        datetimenow = datetime.now()
        # update the growLightIntervals and cameraIntervals with the times of the day 
        if (date.today() > lastUpdatedDate):
            # datetimenow = datetime.now()
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
            # if a new image was captured, publish the image on MQTT broker
            if (lightscamera.newImage):
                print("binary image received")
                index=0
                cameraTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
                df_image = processImageDataForPublishing(suffix_camera, index, lightscamera.filename, lightscamera.binaryImage)
                publishImage(df_image, main_topic+suffix_camera)
                lightscamera.newImage = 0

            # loop to check and run irrigation pumps
            pumps.pollPumps(datetimenow)

        # loop to gather sensor data from all sensors, package it into json, and send it via MQTT 
        if (datetimenow - sensorsLastPolled >= sensorPollingInterval and \
            datetimenow >= datetime.combine(datetimenow.date(), sensor_logging_start) and \
            datetimenow <= datetime.combine(datetimenow.date(), sensor_logging_end)):
            sensorsLastPolled = datetime.now()
            sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
            # temperature and humidity from DHT22 
            index = 0
            for dht in dhts:
                curr_temperature = dht.getTemperature()
                curr_humidity = dht.getHumidity()
                df_temperature = processSensorDataForPublishing(sensorTimeStamp, suffix_temperature, index, curr_temperature)
                saveAndPublishData(df_temperature, main_topic+suffix_temperature)
                df_humidity = processSensorDataForPublishing(sensorTimeStamp, suffix_humidity, index, curr_humidity)
                saveAndPublishData(df_humidity, main_topic+suffix_humidity)
                index += 1
            # light intensity from BH1750 
            curr_lightIntensities = tca.getLightIntensities()
            index = 0
            for li in curr_lightIntensities:
                df_lightintensity = processSensorDataForPublishing(sensorTimeStamp, suffix_lightintensity, index, li)
                saveAndPublishData(df_lightintensity, main_topic+suffix_lightintensity)
                index += 1
            # soil moisture, pH, and EC from soil moisture sensors. PH-4502C, and TDS Meter 1.0 
            curr_soilmoistures = []
            curr_solutionpHs = []
            curr_solutionECs = []
            for ads in adss:
                for sm in ads.getSoilMoistures():
                    curr_soilmoistures.append(sm)
                for pH in ads.getSolutionpHs():
                    curr_solutionpHs.append(pH)
                for ec in ads.getSolutionECs():
                    curr_solutionECs.append(ec)
            index = 0 
            for sm in curr_soilmoistures:
                df_soilmoisture = processSensorDataForPublishing(sensorTimeStamp, suffix_soilmoisture, index, sm)
                saveAndPublishData(df_soilmoisture, main_topic+suffix_soilmoisture)
                index += 1
            index = 0 
            for pH in curr_solutionpHs:
                df_solutionpH = processSensorDataForPublishing(sensorTimeStamp, suffix_pH, index, pH)
                saveAndPublishData(df_solutionpH, main_topic+suffix_pH)
                index += 1
            index = 0 
            for ec in curr_solutionECs:
                df_solutionEC = processSensorDataForPublishing(sensorTimeStamp, suffix_EC, index, ec)
                saveAndPublishData(df_solutionEC, main_topic+suffix_EC)
                index += 1
        
        sleep(1)