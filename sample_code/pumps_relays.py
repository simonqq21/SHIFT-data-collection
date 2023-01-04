'''
switch on the pumps at different intervals
each daily pump interval - time start, time on 

'''

from time import sleep 
import json 
from datetime import datetime, date, time, timedelta
import threading 

pumpIntervals = None 
try:
    j = open("pumps_interval.json")
    pumpIntervals = json.load(j)["pumps"]
except Exception as e:
    print(e)
    print("error opening file, or file doesn't exist")  
print(pumpIntervals) 

try:
    from gpiozero import DigitalOutputDevice
    pumps = []
    pumps.append(DigitalOutputDevice(22))
    pumps.append(DigitalOutputDevice(23))
    pumps.append(DigitalOutputDevice(24))
except:
    print("gpiozero library not present")
    
while True: 
    pass 
