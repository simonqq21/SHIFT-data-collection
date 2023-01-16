'''
MQTT data packet format
{
    'datetime': (datetime object parsed into string),
    'expt_num': (integer),
    'sitename': (string),
    'type': (string eg. "temperature", "humidity", "light_intensity", "soil_moisture", "solution_pH", "solution_EC", "solution_TDS"),
    'count': (integer referring to the total number of sensors),
    'index': (integer),
    'value': (float),
}
'''
import hardware.growlights_camera as growlights_camera
import hardware.irrigation_pumps as irrigation_pumps
import hardware.onewire_temperature_humidity as temperature_humidity 
import hardware.analog_soilmoisture_ph_ec as analog_soilmoisture_ph_ec 
import hardware.i2c_lightintensity as i2c_lightintensity 


print("Starting grow lights and camera loop")
growlights_camera.startGrowLightCameraThread()
print("Starting irrigation pumps loop")
irrigation_pumps.startIrrigationPumpsThread()
print("main")