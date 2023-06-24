import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

import threading
try:
    from gpiozero import Button
except Exception as e:
    print("gpiozero library not present")
    print("Exception = ")
    print(e)
from config import Config

class FunctionButtons:
    def __init__(self):
        self.cameraButton = Button(Config.cameraButtonPin)
        self.pumpButton = Button(Config.pumpButtonPin)

    def setCameraButtonCallback(self, cameraCaptureFunc):
        self.cameraButton.when_pressed = cameraCaptureFunc
    
    def setPumpsButtonCallback(self, pumpsStartFunc):
        self.pumpButton.when_pressed = pumpsStartFunc
    
