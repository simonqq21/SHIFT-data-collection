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
from hardware.growlights_camera import *
from hardware.irrigation_pumps import *
from hardware.onewire_temperature_humidity import getTemperatureValues, getHumidityValues
from hardware.i2c_lightintensity import getLightIntensityValues
from hardware.analog_soilmoisture_ph_ec import getSoilMoistureValues, getpHValues, getECValues

if __name__ == "__main__":
    print(os.getcwd())
    growLightIntervals = loadGrowLightIntervals(os.getcwd()+"/growlight_interval.json")
    cameraIntervals = loadCameraIntervals(os.getcwd()+"/camera_interval.json")
    # datetimenow = datetime.combine(date.today(), time(hour=21, minute=0, second=0))
    datetimenow = datetime.now()
    checkingInterval = timedelta(seconds=10)
    lastUpdatedDate = date(year=1970, month=1, day=1)
    intervalLastChecked = datetime(year=1970, month=1, day=1)

    # get sensor data from all sensors, package it into 
    while True:
        datetimenow = datetime.now()
        # update the growLightIntervals with the times of the day 
        if (date.today() > lastUpdatedDate):
            lastUpdatedDate = date.today() 
            growLightDailyIntervals = getGrowLightIntervalsPerDay(growLightIntervals)
            cameraDailyIntervals = getCameraIntervalsPerDay(cameraIntervals)

        # loop to check the camera and growlights
        if (datetime.now() - intervalLastChecked >= checkingInterval):
            intervalLastChecked = datetime.now()
            # loop to check switch grow lights
            pollGrowLights(growLightDailyIntervals);
            print("val={}".format(growlightval))
            '''
            while the camera is capturing an image, the growlight code must be overriden.
            '''
            # loop to capture image 
            pollCamera(cameraDailyIntervals);
        sleep(1)