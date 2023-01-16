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
    # pumpObject["time_elapsed_since_last_watering"] = timedelta(seconds=99999999)
    pumpObject["time_elapsed_since_last_watering"] = timedelta(seconds=0)
    pumpObject["state"] = False

# create GPIOZero output objects for the pumps
try:
    from gpiozero import DigitalOutputDevice, Button
    pumpObjects[0]["pump"] = DigitalOutputDevice(22)
    pumpObjects[1]["pump"] = DigitalOutputDevice(23)
    pumpObjects[2]["pump"] = DigitalOutputDevice(24) 
    manualWateringButton = Button(10)
except:
    print("gpiozero library not present")

print(pumpObjects) 

'''
# thread function to turn on the pumps for a specified on-time
'''
def pumpOn(pumpObject): 
    print("Manually started irrigation")
    try:
        pumpObject["pump"].on()
    except:  
        print("not running on rpi, switching dummy pump {} on".format(pumpObject["index"]))
    pumpObject["state"] = True
    pumpObject["time_elapsed_since_last_watering"] = timedelta(seconds=pumpObject["on_seconds"].seconds)
    sleep(pumpObject["on_seconds"].seconds)
    try:
        pumpObject["pump"].off()
    except:  
        print("not running on rpi, switching dummy pump {} off".format(pumpObject["index"]))
        pass
    pumpObject["state"] = False

def forceWateringButton(): 
    for pumpObject in pumpObjects: 
        x = threading.Thread(target=pumpOn, args=(pumpObject, ), daemon=True)
        x.start()

try: 
    manualWateringButton.when_pressed = forceWateringButton 
except:
    pass 

datetimenow = datetime.combine(date.today(), time(hour=6, minute=0))
# datetimenow = datetime.now()
while True: 
    for pumpObject in pumpObjects: 
        '''
        water the plants per pump every specified period of time
        the plants will be watered with the specified intervals if either the manual watering button has been pressed,
        or if the time elapsed since watering exceeds the period time and the starting time 
        '''
        if pumpObject["time_elapsed_since_last_watering"] >= pumpObject["period_days"] - timedelta(hours=12) \
            and datetimenow.time().hour == pumpObject["start_time"].hour \
            and datetimenow.time().minute >= pumpObject["start_time"].minute \
            and datetimenow.time().minute <= pumpObject["start_time"].minute + 1:
            x = threading.Thread(target=pumpOn, args=(pumpObject, ), daemon=True)
            x.start()
        elif (not pumpObject["state"]):
            pumpObject["time_elapsed_since_last_watering"] += timeElapsedIncrement 
            print("pump {} timer: {}".format(pumpObject["index"], pumpObject["time_elapsed_since_last_watering"]))
    sleep(pollingMinutes * 60)