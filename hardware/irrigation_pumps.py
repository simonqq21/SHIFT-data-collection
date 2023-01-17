'''
switch on the pumps at different intervals
each daily pump interval - time start, time on, period in days

'''

from time import sleep 
import json 
from datetime import datetime, date, time, timedelta
import threading 

pollingMinutes = 0.1
# pollingMinutes = 1
timeElapsedIncrement = timedelta(seconds=(pollingMinutes * 60)) 

datetimenow = datetime.now()
# datetimenow = datetime.combine(date.today(), time(hour=6, minute=0, second=0))
pumpIntervals = []
# create GPIOZero output objects for the pumps
pumpObjects = []
try:
    from gpiozero import DigitalOutputDevice, Button
    pumpObjects.append(DigitalOutputDevice(22))
    pumpObjects.append(DigitalOutputDevice(23))
    pumpObjects.append(DigitalOutputDevice(24))
    manualWateringButton = Button(10)
except:
    pumpObjects = [0]*3
    print("gpiozero library not present, pumps not added")
    
'''
# thread function to turn on the pumps for a specified on-time
'''
def pumpOn(pumpInterval, pumpObject): 
    print("Manually started irrigation")
    try:
        pumpObject.on()
    except:  
        print("not running on rpi, switching dummy pump {} on".format(pumpInterval["index"]))
    pumpInterval["state"] = True
    pumpInterval["time_elapsed_since_last_watering"] = timedelta(seconds=pumpInterval["on_seconds"].seconds)
    sleep(pumpInterval["on_seconds"].seconds)
    try:
        pumpObject.off()
    except:  
        print("not running on rpi, switching dummy pump {} off".format(pumpInterval["index"]))
        pass
    pumpInterval["state"] = False

def forceWateringButton(): 
    global pumpIntervals
    for i, (pumpInterval, pumpObject) in enumerate(zip(pumpIntervals, pumpObjects)): 
        x = threading.Thread(target=pumpOn, args=(pumpInterval, pumpObject), daemon=True)
        x.start()

def loadPumpsIntervals(filename): # "pumps_interval.json"
    # read pump configuration json file
    global pumpIntervals
    try:
        j = open(filename)
        pumpIntervals = json.load(j)["pumps"]
    except Exception as e:
        print(e)
        print("error opening file, or file doesn't exist")  
    # convert the data into Times and TimeDeltas and add a time_elapsed_since_last_watering element
    for i in range(len(pumpIntervals)):
        pumpIntervals[i]["index"] = i
    for pumpInterval in pumpIntervals: 
        pumpInterval["start_time"] = datetime.strptime(pumpInterval["start_time"], "%H:%M").time()
        pumpInterval["on_seconds"] = timedelta(seconds=pumpInterval["on_seconds"])
        pumpInterval["period_days"] = timedelta(days=pumpInterval["period_days"]) 
        # pumpInterval["time_elapsed_since_last_watering"] = timedelta(seconds=99999999)
        pumpInterval["time_elapsed_since_last_watering"] = timedelta(seconds=0)
        pumpInterval["state"] = False
    print(pumpIntervals) 
    return pumpIntervals 

def pollPumps(pumpIntervals):
    global pumpObjects
    print("0")
    for i, (pumpInterval, pumpObject) in enumerate(zip(pumpIntervals, pumpObjects)): 
        '''
        water the plants per pump every specified period of time
        the plants will be watered with the specified intervals if either the manual watering button has been pressed,
        or if the time elapsed since watering exceeds the period time and the starting time 
        '''
        if pumpInterval["time_elapsed_since_last_watering"] >= pumpInterval["period_days"] - timedelta(hours=12) \
            and datetimenow.time().hour == pumpInterval["start_time"].hour \
            and datetimenow.time().minute >= pumpInterval["start_time"].minute \
            and datetimenow.time().minute <= pumpInterval["start_time"].minute + 1:
            x = threading.Thread(target=pumpOn, args=(pumpInterval, pumpObject), daemon=True)
            x.start()
        elif (not pumpInterval["state"]):
            pumpInterval["time_elapsed_since_last_watering"] += timeElapsedIncrement 
            print("pump {} timer: {}".format(pumpInterval["index"], pumpInterval["time_elapsed_since_last_watering"]))



    
