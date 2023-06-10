'''
switch on the pumps at different durations
each daily pump duration - time start, time on, period in days

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
except:
    print("gpiozero library not present, pumps not added")
from config import Config 

class PumpSystem():
    def __init__(self):
        self.pumps = [] 
        self.pumps.append(Pump(22))
        self.pumps.append(Pump(23))
        self.pumps.append(Pump(24))

    def switchOn(self, pumpIndex, duration):
        self.pumps[pumpIndex].pumpOn(duration)


class Pump():
    def __init__(self, gpio):
        try:
            self.pumpObject = DigitalOutputDevice(gpio)
        except:
            self.pumpObject = None
            print("gpiozero not present, hardware pump not added")
        self.duration = 0
        self.state = 0

    '''
    # thread function to turn on the pumps for a specified on-time
    '''
    def pumpOn(self, duration): 
        self.duration = duration
        print("Manually started irrigation")
        try:
            self.pumpObject.on()
        except:
            print("not running on rpi, switching dummy pump {} on".format(self.duration["index"]))
        finally:
            self.state = 1
        sleep(self.duration)
        try:
            self.pumpObject.off()
        except:  
            print("switching dummy pump {} off".format(self.duration["index"]))
        finally:
            self.state = 0

# (22, 23, 24), 10
            # self.manualWateringButton = Button(buttonGPIO)
            # self.manualWateringButton.when_pressed = self.forceWateringButton 

    # def forceWateringButton(self): 
    #     for pump in self.pumps: 
    #         thread = threading.Thread(target=pump.pumpOn, daemon=True)
    #         thread.start()
