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
                    print(f"Reset growlights timer to {onTime}")             
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

