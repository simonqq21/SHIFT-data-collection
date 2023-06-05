'''
capture and save an 8 MP image from the Raspberry Pi Camera v2
temporarily switch off the purple LED grow lights and switch on the white LED lights
when taking the picture
turn on the purple led grow lights at set intervals
time on and duration on
'''
import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

from time import sleep
from datetime import datetime, date, time, timedelta
import threading
try:
    from gpiozero import DigitalOutputDevice, Button
except Exception as e:
    print("gpiozero library not present")
    print("Exception = ")
    print(e)
from config import Config

class Lights:
    # 18, 27, 9, "growlight_interval.json", "camera_interval.json"
    def __init__(self, growLightGPIO=18, cameraLightGPIO=27): 
        self.growlightval = 0
        self.cameralightval = 0 

        # amount of time in seconds left before the grow light is shut off
        # self.growLightTimeLeft = 0

        # mutex lock for timed growlights 
        self.growLightsLock = threading.Lock()

        # initialize GPIOzero outputs
        try:
            self.growlight = DigitalOutputDevice(growLightGPIO)
            self.cameralight = DigitalOutputDevice(cameraLightGPIO)
            # self.cameraButton = Button(cameraButtonGPIO)
        except Exception as e:
            print("not running on pi, failed to initialize growlights and cameralights")
            print(e)

        self.purpleOnTime = 0 
        self.whiteOnTime = 0

    '''
    switch the ON/OFF state of the grow lights
    '''
    def switchGrowLights(self, state):
        self.growlightval = state
        try:
            if state:
                self.growlight.on()
            else:
                self.growlight.off()
        except Exception as e: 
            print("not running on rpi, switching dummy growlights")
        if Config.debug:
            if state:
                print("growlight on")
            else:
                print("growlight off")

    '''
    switch the ON/OFF state of the camera lights 
    '''
    def switchCameraLights(self, state):
        self.cameralightval = state
        try:
            if state:
                self.cameralight.on()
            else:
                self.cameralight.off()
        except Exception as e: 
            print("not running on rpi, switching dummy cameralights")
        if Config.debug:
            if state:
                print("cameralight on")
            else:
                print("cameralight off")

    '''
    thread function to switch on the grow lights for a certain duration, used for timing
    '''
    def growLightOn(self, onTime):
        self.purpleOnTime = onTime
        if self.purpleOnTime > 0:
            if self.growLightsLock.locked():
                if Config.debug:
                    print("growlights timer already running!") 
            else:
                # acquire the timed growlight lock
                self.growLightsLock.acquire()
                self.switchGrowLights(1)
                while (self.purpleOnTime > 0):
                    sleep(1)
                    if Config.debug:
                        print("{}s of purple light left".format(self.purpleOnTime))
                    self.purpleOnTime -= 1
                self.switchGrowLights(0)
                # release the timed growlight lock 
                self.growLightsLock.release()
        elif self.purpleOnTime == 0:
            self.switchGrowLights(0)
        else:
            self.switchGrowLights(1)
    

    '''
    thread function to switch on the camera lights for a certain duration, used for timing
    '''
    def cameraLightOn(self, onTime):
        self.whiteOnTime = onTime
        if self.whiteOnTime > 0:
            self.growLightsLock
            self.switchCameraLights(1)
            while (self.whiteOnTime > 0):
                sleep(1)
                if Config.debug:
                    print("{}s of white light left".format(self.whiteOnTime))
                self.whiteOnTime -= 1
            self.switchCameraLights(0)
        elif self.whiteOnTime == 0:
            self.switchCameraLights(0)
        else:
            self.switchCameraLights(1)


    '''
    thread function to toggle the grow lights and camera lights to capture an image using the Pi Camera
    '''
    def flashCameraLight(self, flashTime):
        # save the growlights state and turn off the growlights
        growLightsWereOn = False 
        if (self.growlightval):
            growLightsWereOn = True
        self.switchGrowLights(0) 
        self.cameraLightOn(flashTime)
        # revert the growlights state
        if (growLightsWereOn and self.purpleOnTime > 0):
            self.switchGrowLights(1)



















#     '''
#     method to set the camera light operation to manual ON, manual OFF, or AUTO.
#     '''
#     def setCameraLightOperation(self, mode):
#         if mode == 1:
#             # set camera light to manual 
#             self.cameraLightMode = 0 
#             self.switchCameraLights(1)
            
#         elif mode == 0:
#             self.cameraLightMode = 0 
#             self.switchCameraLights(0) 

#         elif mode == 2: 
#             # set camera light to automatic 
#             self.cameraLightMode = 1

#     '''
#     method to set the grow light operation to manual ON, manual OFF, or AUTO.
#     '''
#     def setGrowLightOperation(self, mode):
#         if mode == 1:
#             # set grow light to manual 
#             self.growLightMode = 0 
#             self.switchGrowLights(1) 

#         elif mode == 0:
#             self.growLightMode = 0 
#             self.switchGrowLights(0)  

#         elif mode == 2:
#             # set grow light to automatic 
#             self.growLightMode = 1 

#     # thread function to toggle the grow lights and camera lights and capture an image using the Pi Camera
#     def captureImage(self, filepath=None, filename=None):
#         self.imageStream = BytesIO()
#         self.binaryImage = None
#         self.pictureTaking = 1
#         growLightsWereOn = False 
#         if (self.growlightval):
#             growLightsWereOn = True
#         self.switchGrowLights(0)  
#         # only automatically switch camera lights on if the camera light is set to auto
#         if (self.cameraLightMode):
#             self.switchCameraLights(1)
#         if filepath is None:
#             filepath=self.images_filepath 
#         if filename is None:
#             self.filename=self.image_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
#         else:
#             self.filename = filename
#         try:
#             self.camera.start_preview() 
#             sleep(2)
#             self.camera.capture(self.imageStream, 'jpeg')
#             with open(filepath + self.filename, "wb") as f:
#                 f.write(self.imageStream.getbuffer())
#             f.close()
#             self.binaryImage = binascii.b2a_base64(self.imageStream.getvalue()).decode()
#         except:
#             print("no camera object, using dummy camera")
#         print("image captured")
#         sleep(0.5)
#         # only automatically switch camera lights off if the camera light is set to auto
#         if (self.cameraLightMode):
#             self.switchCameraLights(0)
#         if (growLightsWereOn):
#             self.switchGrowLights(1)
#         try:
#             self.camera.stop_preview()
#         except:
#             pass
#         self.pictureTaking = 0
#         self.newImage = 1
#         return self.binaryImage

#     #wrapper function to capture an image every time the capture button is pressed 
#     def captureImageButton(self):
#         # change the filepath and filename
#         thread = threading.Thread(target=self.captureImage, daemon=True)
#         thread.start()

#     def pollGrowLights(self, datetimenow):
#         # loop to check switch grow lights
#         for dayinterval in self.growLightDailyIntervals:
#             # If the time is between the on and off time and the grow lights are off, switch them on.
#             print("{},{},{},{},".format(datetimenow >= dayinterval["on_time"], \
#                 datetimenow < dayinterval["off_time"], \
#                 self.growlightval, \
#                 self.pictureTaking))
#             print()
#             if (datetimenow >= dayinterval["on_time"] \
#                 and datetimenow < dayinterval["off_time"] \
#                 and not self.growlightval \
#                 and not self.pictureTaking):
#                 actualOnInterval = dayinterval["duration"] - (datetimenow - dayinterval["on_time"])
#                 thread = threading.Thread(target=self.growLightOn, args=(actualOnInterval, ), daemon=True)
#                 thread.start()

#     def pollCamera(self, datetimenow):
#         # loop to capture image 
#         for dayinterval in self.cameraDailyIntervals: 
#             if (datetimenow >= dayinterval["start_time"] \
#                 and datetimenow <= dayinterval["end_time"] \
#                 and datetime.now() - self.lastTimePhotoTaken >= dayinterval["interval"]):
#                 self.lastTimePhotoTaken = datetime.now()
#                 # change the filepath and filename
#                 thread = threading.Thread(target=self.captureImage, daemon=True)
#                 thread.start()

