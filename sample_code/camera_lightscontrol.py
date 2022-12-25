'''
capture and save an 8 MP image from the Raspberry Pi Camera v2
temporarily switch off the purple LED grow lights and switch on the white LED lights
when taking the picture
turn on the purple led grow lights at set intervals
time on and duration on
'''

from time import sleep
import json
from datetime import datetime, date, time, timedelta
import threading
try:
    from picamera import PiCamera
    from gpiozero import DigitalOutputDevice
except:
    print("picamera or gpiozero library not present")

global growlightval
growlightval = 0

try:
    camera = PiCamera()
    try:
        camera.resolution = (3280, 2464)
    except Exception as err:
        camera.resolution = (2592, 1944)
except:
    print("Failed to create camera object!")

# load intervals of grow lights
j = open("growlight_interval.json")
intervals = json.load(j)["intervals"]

def getOnIntervalsPerDay(intervals):
    dayintervals = [] 
    for interval in intervals: 
        newDayInterval = {} 
        newDayInterval["on_time"] = datetime.combine(date.today(), interval["on_time"])
        newDayInterval["duration"] = interval["duration"]
        newDayInterval["off_time"] = newDayInterval["on_time"] + interval["duration"]
        dayintervals.append(newDayInterval)
    return dayintervals

lastUpdatedDate = date.today() 
for interval in intervals:
    interval["on_time"] = datetime.strptime(interval["on_time"], "%H:%M").time()
    interval["duration"] = timedelta(hours=int(interval["duration"][:2]), minutes=int(interval["duration"][3:]))
    # ensure that duration doesn't exceed 24h
    if (interval["duration"] > timedelta(hours=24)):
        interval["duration"] = timedelta(hours=24)
print(intervals)
dayintervals = getOnIntervalsPerDay(intervals) 
print(dayintervals)


def growLightOn(ondelta):
    global growlightval
    print("growlight on")
    # growlight.on()
    growlightval=1
    print("g")
    sleep(ondelta.seconds)
    print("growlight off")
    # growlight.off()

def captureImage(filepath, filename):
    # growlight.off()
    # cameralight.on()
    camera.start_preview() 
    time.sleep(2)
    camera.capture(filepath, filename)
    time.sleep(0.5)
    # cameralight.off()
    # growlight.on()

# debugging
datetimenow = datetime.combine(date.today(), time(hour=10, minute=0, second=0))
while True:
    # switch on the grow lights during the specified interval

    # update the intervals with the times of the day 
    if (date.today() > lastUpdatedDate):
        lastUpdatedDate = date.today() 
        dayintervals = getOnIntervalsPerDay(intervals)

    # loop to control grow lights
    for dayinterval in dayintervals:
        # if the time is between the on
        
        if (datetimenow >= dayinterval["on_time"] \
            and datetimenow < dayinterval["off_time"] \
            # and not growlight.value \
            and not growlightval \
        ):
            thread = threading.Thread(target=growLightOn, args=(dayinterval["duration"], ), daemon=True)
            # growlightval=1
            thread.start()
    print(growlightval)
    sleep(1)

# growlight = DigitalOutputDevice(18)
# cameralight = DigitalOutputDevice(27)
#
# time.sleep(5)

