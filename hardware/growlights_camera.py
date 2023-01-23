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
from io import BytesIO
try:
    from picamera import PiCamera
    from gpiozero import DigitalOutputDevice, Button
except Exception as e:
    print("picamera or gpiozero library not present")
    print("Exception = ")
    print(e)
import os 
import binascii

# image filepath and filename 
images_filepath = "/home/pi/images/"
images_filename_format = "IMG_{}.jpg"
# create image filepath if it doesn't exist 
os.makedirs(images_filepath, exist_ok=True)

class LightsCamera:
    # 18, 27, 9, "growlight_interval.json", "camera_interval.json"
    def __init__(self, growLightGPIO, cameraLightGPIO, cameraButtonGPIO, growLightsIntervalsFilename, cameraIntervalsFilename): 
        self.growlightval = 0
        self.cameralightval = 0 
        self.pictureTaking = 0 
        self.imageStream = BytesIO()
        self.binaryImage = None
        self.newImage = 0
        # flag to indicate if an image is currently being captured
        self.lastTimePhotoTaken = datetime(year=1970, month=1, day=1)

        # initialize GPIOzero outputs
        try:
            self.growlight = DigitalOutputDevice(growLightGPIO)
            self.cameralight = DigitalOutputDevice(cameraLightGPIO)
            self.cameraButton = Button(cameraButtonGPIO)
        except Exception as e:
            print("not running on pi, failed to initialize growlights and cameralights")
            print(e)

        try:
            print("setting manual camera capture button callback")
            self.cameraButton.when_pressed = self.captureImageButton 
        except Exception as e:
            print(e)
            pass

        # initialize camera object
        try:
            self.camera = PiCamera()
            try:
                self.amera.resolution = (3280, 2464)
            except Exception as err:
                self.camera.resolution = (2592, 1944)
        except:
            print("Failed to create camera object!")

        self.loadGrowLightIntervals(growLightsIntervalsFilename)
        self.loadCameraIntervals(cameraIntervalsFilename)
        self.getGrowLightIntervalsPerDay()
        self.getCameraIntervalsPerDay()

    # load intervals of grow lights
    def loadGrowLightIntervals(self, filename):
        self.growLightIntervals = None
        try:
            j = open(filename)
            self.growLightIntervals = json.load(j)["intervals"]
        except:
            print("error opening file, or file doesn't exist") 
        # initial processing of grow light intervals 
        lastUpdatedDate = date.today() 
        for interval in self.growLightIntervals:
            interval["on_time"] = datetime.strptime(interval["on_time"], "%H:%M").time()
            interval["duration"] = timedelta(hours=int(interval["duration"][:2]), minutes=int(interval["duration"][3:]))
            # ensure that duration doesn't exceed 24h
            if (interval["duration"] > timedelta(hours=24)):
                interval["duration"] = timedelta(hours=24)
        print(self.growLightIntervals)

    # load intervals of image capture 
    def loadCameraIntervals(self, filename): 
        self.cameraIntervals = None
        try:
            j = open(filename)
            self.cameraIntervals = json.load(j)["intervals"]
        except:
            print("error opening file, or file doesn't exist")  
        # initial processing of camera intervals 
        for interval in self.cameraIntervals:
            interval["start_time"] = datetime.strptime(interval["start_time"], "%H:%M").time()
            interval["interval"] = timedelta(hours=int(interval["interval"][:2]), minutes=int(interval["interval"][3:]))
            interval["end_time"] = datetime.strptime(interval["end_time"], "%H:%M").time()
        print(self.cameraIntervals)

    # compute for the grow light intervals for each new day
    def getGrowLightIntervalsPerDay(self):
        self.growLightDailyIntervals = [] 
        for interval in self.growLightIntervals: 
            newGrowLightInterval = {} 
            newGrowLightInterval["on_time"] = datetime.combine(date.today(), interval["on_time"])
            newGrowLightInterval["duration"] = interval["duration"]
            newGrowLightInterval["off_time"] = newGrowLightInterval["on_time"] + interval["duration"]
            self.growLightDailyIntervals.append(newGrowLightInterval)
        print(self.growLightDailyIntervals)

    # compute for the image capturing intervals for each new day
    def getCameraIntervalsPerDay(self):
        self.cameraDailyIntervals = []
        for interval in self.cameraIntervals: 
            newCameraInterval = {}
            newCameraInterval["start_time"] = datetime.combine(date.today(), interval["start_time"]) 
            newCameraInterval["interval"] = interval["interval"]
            newCameraInterval["end_time"] = datetime.combine(date.today(), interval["end_time"]) 
            self.cameraDailyIntervals.append(newCameraInterval)
        print(self.cameraDailyIntervals)

    # switch the state of the grow lights
    def switchGrowLights(self, state):
        self.growlightval = state
        try:
            if state:
                self.growlight.on()
            else:
                self.growlight.off()
        except Exception as e: 
            print("not running on rpi, switching dummy growlights")
        if state:
            print("growlight on")
        else:
            print("growlight off")

    # switch the state of the camera lights 
    def switchCameraLights(self, state):
        self.cameralightval = state
        try:
            if state:
                self.cameralight.on()
            else:
                self.cameralight.off()
        except Exception as e: 
            print("not running on rpi, switching dummy cameralights")
            
        if state:
            print("cameralight on")
        else:
            print("cameralight off")

    # thread function to switch on the grow lights for a certain duration
    def growLightOn(self, ondelta):
        sleeptime = ondelta.seconds
        self.switchGrowLights(1)
        while (sleeptime > 0):
            sleep(1)
            print("{}s of light left".format(sleeptime))
            sleeptime -= 1
        self.switchGrowLights(0)

    # thread function to toggle the grow lights and camera lights and capture an image using the Pi Camera
    def captureImage(self, filepath, filename):
        self.imageStream = BytesIO()
        self.binaryImage = None
        self.pictureTaking = 1
        growLightsWereOn = False 
        if (self.growlightval):
            growLightsWereOn = True
        self.switchGrowLights(0)
        self.switchCameraLights(1)
        try:
            self.camera.start_preview() 
            sleep(2)
            self.camera.capture(self.imageStream, 'jpeg')
            with open(filepath + filename, "wb") as f:
                f.write(self.imageStream.getbuffer())
            f.close()
            self.binaryImage = binascii.b2a_base64(self.imageStream.getvalue()).decode()
        except:
            print("no camera object, using dummy camera")
        print("image captured")
        sleep(0.5)
        self.switchCameraLights(0)
        if (growLightsWereOn):
            self.switchGrowLights(1)
        try:
            self.camera.stop_preview()
        except:
            pass
        self.pictureTaking = 0
        self.newImage = 1
        return self.binaryImage

    #wrapper function to capture an image every time the capture button is pressed 
    def captureImageButton(self):
        # change the filepath and filename
        image_filename = images_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
        thread = threading.Thread(target=self.captureImage, args=(images_filepath, image_filename), daemon=True)
        thread.start()

    def pollGrowLights(self, datetimenow):
        # loop to check switch grow lights
        for dayinterval in self.growLightDailyIntervals:
            # If the time is between the on and off time and the grow lights are off, switch them on.
            print("{},{},{},{},".format(datetimenow >= dayinterval["on_time"], \
                datetimenow < dayinterval["off_time"], \
                self.growlightval, \
                self.pictureTaking))
            print()
            if (datetimenow >= dayinterval["on_time"] \
                and datetimenow < dayinterval["off_time"] \
                and not self.growlightval \
                and not self.pictureTaking):
                actualOnInterval = dayinterval["duration"] - (datetimenow - dayinterval["on_time"])
                thread = threading.Thread(target=self.growLightOn, args=(actualOnInterval, ), daemon=True)
                thread.start()

    def pollCamera(self, datetimenow):
        # loop to capture image 
        for dayinterval in self.cameraDailyIntervals: 
            if (datetimenow >= dayinterval["start_time"] \
                and datetimenow <= dayinterval["end_time"] \
                and datetime.now() - self.lastTimePhotoTaken >= dayinterval["interval"]):
                self.lastTimePhotoTaken = datetime.now()
                # change the filepath and filename
                image_filename = images_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
                thread = threading.Thread(target=self.captureImage, args=(images_filepath, image_filename), daemon=True)
                thread.start()

