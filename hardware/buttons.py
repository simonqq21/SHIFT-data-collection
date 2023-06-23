import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

from time import sleep
from datetime import datetime, date, time, timedelta
import threading
try:
    from gpiozero import Button
except Exception as e:
    print("gpiozero library not present")
    print("Exception = ")
    print(e)
from config import Config

class SystemButtons:
    def __init__(self):
        self.cameraButton = Button(Config.cameraButtonPin)
        self.pumpButton = Button(Config.pumpButtonPin)

    def setCameraButtonCallback(self, func, 
