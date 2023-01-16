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
import hardware.growlights_camera 
import hardware.irrigation_pumps