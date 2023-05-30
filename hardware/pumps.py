'''
switch on the pumps at different durations
each daily pump duration - time start, time on, period in days

'''
import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..')) 

from time import sleep 
import json 
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
        # self.duration["state"] = True
        # self.duration["time_elapsed_since_last_watering"] = timedelta(seconds=self.duration["on_seconds"].seconds)
        # sleep(self.duration["on_seconds"].seconds)
        sleep(self.duration)
        try:
            self.pumpObject.off()
        except:  
            print("switching dummy pump {} off".format(self.duration["index"]))
            pass
        self.duration["state"] = False

# (22, 23, 24), 10, "pumps_duration.json" 


            # self.manualWateringButton = Button(buttonGPIO)
            # self.manualWateringButton.when_pressed = self.forceWateringButton 

    # def loadPumpsdurations(self, filename): # "pumps_duration.json"
    #     self.pumpdurations = []
    #     # read pump configuration json file
    #     try:
    #         j = open(filename)
    #         self.pumpdurations = json.load(j)["pumps"]
    #     except Exception as e:
    #         print(e)
    #         print("error opening file, or file doesn't exist")  
    #     # convert the data into Times and TimeDeltas and add a time_elapsed_since_last_watering element
    #     for i in range(len(self.pumpdurations)):
    #         self.pumpdurations[i]["index"] = i
    #     for pumpduration in self.pumpdurations: 
    #         pumpduration["start_time"] = datetime.strptime(pumpduration["start_time"], "%H:%M").time()
    #         pumpduration["on_seconds"] = timedelta(seconds=pumpduration["on_seconds"])
    #         pumpduration["period_days"] = timedelta(days=pumpduration["period_days"]) 
    #         # pumpduration["time_elapsed_since_last_watering"] = timedelta(seconds=99999999)
    #         pumpduration["time_elapsed_since_last_watering"] = timedelta(seconds=0)
    #         pumpduration["state"] = False
    #     print(self.pumpdurations) 

    # def forceWateringButton(self): 
    #     for pump in self.pumps: 
    #         thread = threading.Thread(target=pump.pumpOn, daemon=True)
    #         thread.start()

    # def pollPumps(self, datetimenow):
    #     for pump in self.pumps: 
    #         '''
    #         water the plants per pump every specified period of time
    #         the plants will be watered with the specified durations if either the manual watering button has been pressed,
    #         or if the time elapsed since watering exceeds the period time and the starting time 
    #         '''
    #         if pump.duration["time_elapsed_since_last_watering"] >= pump.duration["period_days"] - timedelta(hours=12) \
    #             and datetimenow.time().hour == pump.duration["start_time"].hour \
    #             and datetimenow.time().minute >= pump.duration["start_time"].minute \
    #             and datetimenow.time().minute <= pump.duration["start_time"].minute + 1:
    #             thread = threading.Thread(target=pump.pumpOn, daemon=True)
    #             thread.start()
    #         elif (not pump.duration["state"]):
    #             pump.duration["time_elapsed_since_last_watering"] += timeElapsedIncrement 
    #             print("pump {} timer: {}".format(pump.duration["index"], pump.duration["time_elapsed_since_last_watering"]))



        
