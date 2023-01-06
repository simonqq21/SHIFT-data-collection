'''
switch on the pumps at different intervals
each daily pump interval - time start, time on 

'''

from time import sleep 
import json 
from datetime import datetime, date, time, timedelta
import threading 

pollingMinutes = 1
timeElapsedIncrement = timedelta(seconds=(pollingMinutes * 60)) 

# read pump configuration json file
pumpObjects = None 
try:
    j = open("pumps_interval.json")
    pumpObjects = json.load(j)["pumps"]
except Exception as e:
    print(e)
    print("error opening file, or file doesn't exist")  
print(pumpObjects) 

# convert the data into Times and TimeDeltas and add a time_elapsed_since_last_watering element
for pumpObject in pumpObjects: 
    pumpObject["start_time"] = datetime.strptime(pumpObject["start_time"], "%H:%M").time()
    pumpObject["on_seconds"] = timedelta(seconds=pumpObject["on_seconds"])
    pumpObject["period_days"] = timedelta(days=pumpObject["period_days"]) 
    pumpObject["time_elapsed_since_last_watering"] = timedelta(seconds=0)

# create GPIOZero output objects for the pumps
try:
    from gpiozero import DigitalOutputDevice
    pumpObjects[0]["pump"] = DigitalOutputDevice(22)
    pumpObjects[1]["pump"] = DigitalOutputDevice(23)
    pumpObjects[2]["pump"] = DigitalOutputDevice(24)
except:
    print("gpiozero library not present")

print(pumpObjects) 


'''
# thread function to turn on the pumps for a specified on-time
'''
def pumpOn(pumpObject): 
    try:
        pumpObject["pump"].on()
    except:  
        print("not running on rpi, switching dummy pump {} on".format(pumpObject["index"]))
    pumpObject["time_elapsed_since_last_watering"] = timedelta(seconds=pumpObject["on_seconds"].seconds)
    sleep(pumpObject["on_seconds"].seconds)
    try:
        pumpObject["pump"].off()
    except:  
        print("not running on rpi, switching dummy pump {} off".format(pumpObject["index"]))
        pass

datetimenow = datetime.combine(date.today(), time(hour=6, minute=0))
# datetimenow = datetime.now()
while True: 
    for pumpObject in pumpObjects: 
        # water the plants per pump every specified period of time
        if pumpObject["time_elapsed_since_last_watering"] >= pumpObject["period_days"] and datetimenow.time() == pumpObject["start_time"]:
            x = threading.Thread(target=pumpOn, args=(pumpObject, ), daemon=True)
            x.start()
        elif (not pumpObject["pump"].value):
            pumpObject["time_elapsed_since_last_watering"] += timeElapsedIncrement
    sleep(pollingMinutes * 60)