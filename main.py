'''
MQTT data packet format
{
    'datetime': (datetime object parsed into string),
    'expt_num': (integer),
    'sitename': (string),
    'type': (string eg. "temperature", "humidity", "light_intensity", "soil_moisture",  
            solution_pH", "solution_EC", "solution_TDS"),
    'count': (integer referring to the total number of sensors),
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
from hardware.i2c_lightintensity import getLightIntensityValues
from hardware.analog_soilmoisture_ph_ec import getSoilMoistureValues, getpHValues, getECValues

if __name__ == "__main__":
    print(os.getcwd())
    lightscamera = LightsCamera(18, 27, 9, os.getcwd()+"/growlight_interval.json", os.getcwd()+"/camera_interval.json")
    pumps = SyncedPumps((22, 23, 24), 10, os.getcwd()+"/pumps_interval.json")
    # datetimenow = datetime.combine(date.today(), time(hour=21, minute=0, second=0))
    # datetimenow = datetime.combine(date.today(), time(hour=5, minute=59, second=50))
    datetimenow = datetime.now()
    checkingInterval = timedelta(seconds=10)
    lastUpdatedDate = date(year=1970, month=1, day=1)
    intervalLastChecked = datetime(year=1970, month=1, day=1)
    # sensorsLastPolled = 
    
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
                print("binary image received")
                # print("binary image = {}".format(lightscamera.binaryImage))
                lightscamera.newImage = 0

            # loop to check and run irrigation pumps
            pumps.pollPumps(datetimenow)

        # loop to gather sensor data from all sensors, package it into json, and send it via MQTT 
        # temperature and humidity from DHT22 

        # light intensity from BH1750 

        # soil moisture, pH, and EC from soil moisture sensors. PH-4502C, and TDS Meter 1.0 

        
        sleep(1)