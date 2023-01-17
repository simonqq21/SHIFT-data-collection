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
    from gpiozero import DigitalOutputDevice, Button
except Exception as e:
    print("picamera or gpiozero library not present")
    print("Exception = ")
    print(e)
import os 

# image filepath and filename 
images_filepath = "/home/pi/images/"
images_filename_format = "IMG_{}.jpg"
# create image filepath if it doesn't exist 
os.makedirs(images_filepath, exist_ok=True)

# dummy values
growlightval = 0
cameralightval = 0
# flag to indicate if an image is currently being captured
pictureTaking = 0

lastTimePhotoTaken = datetime(year=1970, month=1, day=1)
# datetimenow = datetime.combine(date.today(), time(hour=6, minute=0, second=0))
datetimenow = datetime.now()

# initialize GPIOzero outputs
try:
    growlight = DigitalOutputDevice(18)
    cameralight = DigitalOutputDevice(27)
    cameraButton = Button(9)
    cameraButton.when_pressed = captureImageButton 
except Exception as e:
    print("not running on pi, using dummy output values")
    print(e)

# initialize camera object
try:
    camera = PiCamera()
    try:
        camera.resolution = (3280, 2464)
    except Exception as err:
        camera.resolution = (2592, 1944)
except:
    print("Failed to create camera object!")

# load intervals of grow lights
def loadGrowLightIntervals(filename): # "growlight_interval.json"
    growLightIntervals = None
    try:
        j = open(filename)
        growLightIntervals = json.load(j)["intervals"]
    except:
        print("error opening file, or file doesn't exist") 
    # initial processing of grow light intervals 
    lastUpdatedDate = date.today() 
    for interval in growLightIntervals:
        interval["on_time"] = datetime.strptime(interval["on_time"], "%H:%M").time()
        interval["duration"] = timedelta(hours=int(interval["duration"][:2]), minutes=int(interval["duration"][3:]))
        # ensure that duration doesn't exceed 24h
        if (interval["duration"] > timedelta(hours=24)):
            interval["duration"] = timedelta(hours=24)
    # print(growLightIntervals)
    return growLightIntervals

# load intervals of image capture 
def loadCameraIntervals(filename): # "camera_interval.json"
    cameraIntervals = None
    try:
        j = open(filename)
        cameraIntervals = json.load(j)["intervals"]
    except:
        print("error opening file, or file doesn't exist")  
    # initial processing of camera intervals 
    for interval in cameraIntervals:
        interval["start_time"] = datetime.strptime(interval["start_time"], "%H:%M").time()
        interval["interval"] = timedelta(hours=int(interval["interval"][:2]), minutes=int(interval["interval"][3:]))
        interval["end_time"] = datetime.strptime(interval["end_time"], "%H:%M").time()
    return cameraIntervals
    
# compute for the grow light intervals for each new day
def getGrowLightIntervalsPerDay(intervals):
    growLightIntervals = [] 
    for interval in intervals: 
        newGrowLightInterval = {} 
        newGrowLightInterval["on_time"] = datetime.combine(date.today(), interval["on_time"])
        newGrowLightInterval["duration"] = interval["duration"]
        newGrowLightInterval["off_time"] = newGrowLightInterval["on_time"] + interval["duration"]
        growLightIntervals.append(newGrowLightInterval)
    return growLightIntervals

# compute for the image capturing intervals for each new day
def getCameraIntervalsPerDay(intervals):
    cameraIntervals = []
    for interval in intervals: 
        newCameraInterval = {}
        newCameraInterval["start_time"] = datetime.combine(date.today(), interval["start_time"]) 
        newCameraInterval["interval"] = interval["interval"]
        newCameraInterval["end_time"] = datetime.combine(date.today(), interval["end_time"]) 
        cameraIntervals.append(newCameraInterval)
    return cameraIntervals

# switch the state of the grow lights
def switchGrowLights(state):
    global growlightval
    growlightval = state
    try:
        if state:
            growlight.on()
        else:
            growlight.off()
    except Exception as e: 
        print("not running on rpi, switching dummy growlights")
    if state:
        print("growlight on")
    else:
        print("growlight off")

# switch the state of the camera lights 
def switchCameraLights(state):
    global cameralightval
    try:
        if state:
            cameralight.on()
        else:
            cameralight.off()
    except Exception as e: 
        print("not running on rpi, switching dummy cameralights")
        cameralightval = state
    if state:
        print("cameralight on")
    else:
        print("cameralight off")

# thread function to switch on the grow lights for a certain duration
def growLightOn(ondelta):
    sleeptime = ondelta.seconds
    switchGrowLights(1)
    while (sleeptime > 0):
        sleep(1)
        print("{}s of light left".format(sleeptime))
        sleeptime -= 1
    switchGrowLights(0)

# thread function to toggle the grow lights and camera lights and capture an image using the Pi Camera
def captureImage(filepath, filename):
    pictureTaking = 1
    growLightsWereOn = False 
    if (growlightval):
        growLightsWereOn = True
    switchGrowLights(0)
    switchCameraLights(1)
    try:
        camera.start_preview() 
    except:
        print("no camera object, using dummy camera")
    sleep(2)
    try:
        camera.capture(filepath + filename)
    except:
        pass
    print("image captured")
    sleep(0.5)
    switchCameraLights(0)
    if (growLightsWereOn):
        switchGrowLights(1)
    try:
        camera.stop_preview()
    except:
        pass
    pictureTaking = 0

#wrapper function to capture an image every time the capture button is pressed 
def captureImageButton():
    # change the filepath and filename
    image_filename = images_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
    thread = threading.Thread(target=captureImage, args=(images_filepath, image_filename), daemon=True)
    thread.start()

try:
    cameraButton.when_pressed = captureImageButton 
except:
    pass

def pollGrowLights(growLightDailyIntervals):
    global datetimenow
    # loop to check switch grow lights
    for dayinterval in growLightDailyIntervals:
        # If the time is between the on and off time and the grow lights are off, switch them on.
        if (datetimenow >= dayinterval["on_time"] \
            and datetimenow < dayinterval["off_time"] \
            and not growlightval and not pictureTaking):
            thread = threading.Thread(target=growLightOn, args=(dayinterval["duration"], ), daemon=True)
            thread.start()

def pollCamera(cameraDailyIntervals):
    global datetimenow, lastTimePhotoTaken
    # loop to capture image 
    for dayinterval in cameraDailyIntervals: 
        if (datetimenow >= dayinterval["start_time"] \
            and datetimenow <= dayinterval["end_time"] \
            and datetime.now() - lastTimePhotoTaken >= dayinterval["interval"]):
            lastTimePhotoTaken = datetime.now()
            # change the filepath and filename
            image_filename = images_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
            thread = threading.Thread(target=captureImage, args=(images_filepath, image_filename), daemon=True)
            thread.start()

