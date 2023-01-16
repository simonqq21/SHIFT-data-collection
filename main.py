'''
MQTT data packet format
{
    'datetime': (datetime object parsed into string),
    'expt_num': (integer),
    'sitename': (string),
    'type': (string eg. "temperature", "humidity", "light_intensity"),
    'count': (integer referring to the total number of sensors),
    'values': (list of dicts as shown in line 11),
}

[   
    {   
        'index': 0,
        'temperature_value': 27.8
    },
    {
        'index': 1,
        'temperature_value': 28.0
    },
    {
        ...
    },
    ...
]

The value key in values such as in line 14 can be one of the ff.:
[   'temperature_value',
    'humidity_value',
    'pH_value',
    'TDS_value',
    'EC_value',
    'soilmoisture_value',
    'lightintensity_value'  
]

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