'''
switch on the pumps at different intervals
each daily pump interval - time start, time on, period in days

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
pollingMinutes = 1/6
timeElapsedIncrement = timedelta(seconds=(pollingMinutes * 60)) 

class Pump():
    def __init__(self, gpio, interval):
        try:
            self.pumpObject = DigitalOutputDevice(gpio)
        except:
            self.pumpObject = None
            print("gpiozero not present, hardware pump not added")
        self.interval = interval

    '''
    # thread function to turn on the pumps for a specified on-time
    '''
    def pumpOn(self): 
        print("Manually started irrigation")
        try:
            self.pumpObject.on()
        except:  
            print("not running on rpi, switching dummy pump {} on".format(self.interval["index"]))
        self.interval["state"] = True
        self.interval["time_elapsed_since_last_watering"] = timedelta(seconds=self.interval["on_seconds"].seconds)
        sleep(self.interval["on_seconds"].seconds)
        try:
            self.pumpObject.off()
        except:  
            print("switching dummy pump {} off".format(self.interval["index"]))
            pass
        self.interval["state"] = False

class SyncedPumps:
    # (22, 23, 24), 10, "pumps_interval.json"
    def __init__(self, pumpGPIOs, buttonGPIO, pumpIntervalsFilename):
        self.pumpIntervals = []
        self.loadPumpsIntervals(pumpIntervalsFilename)
        self.pumps = []
        # create GPIOZero output objects for the pumps
        try:
            for i, (gpio, interval) in enumerate(zip(pumpGPIOs, self.pumpIntervals)):
                self.pumps.append(Pump(gpio, interval))
            self.manualWateringButton = Button(buttonGPIO)
            self.manualWateringButton.when_pressed = self.forceWateringButton 
        except:
            print("gpiozero not present, pumps not added")
    
    def loadPumpsIntervals(self, filename): # "pumps_interval.json"
        self.pumpIntervals = []
        # read pump configuration json file
        try:
            j = open(filename)
            self.pumpIntervals = json.load(j)["pumps"]
        except Exception as e:
            print(e)
            print("error opening file, or file doesn't exist")  
        # convert the data into Times and TimeDeltas and add a time_elapsed_since_last_watering element
        for i in range(len(self.pumpIntervals)):
            self.pumpIntervals[i]["index"] = i
        for pumpInterval in self.pumpIntervals: 
            pumpInterval["start_time"] = datetime.strptime(pumpInterval["start_time"], "%H:%M").time()
            pumpInterval["on_seconds"] = timedelta(seconds=pumpInterval["on_seconds"])
            pumpInterval["period_days"] = timedelta(days=pumpInterval["period_days"]) 
            # pumpInterval["time_elapsed_since_last_watering"] = timedelta(seconds=99999999)
            pumpInterval["time_elapsed_since_last_watering"] = timedelta(seconds=0)
            pumpInterval["state"] = False
        print(self.pumpIntervals) 

    def forceWateringButton(self): 
        for pump in self.pumps: 
            thread = threading.Thread(target=pump.pumpOn, daemon=True)
            thread.start()

    def pollPumps(self, datetimenow):
        for pump in self.pumps: 
            '''
            water the plants per pump every specified period of time
            the plants will be watered with the specified intervals if either the manual watering button has been pressed,
            or if the time elapsed since watering exceeds the period time and the starting time 
            '''
            if pump.interval["time_elapsed_since_last_watering"] >= pump.interval["period_days"] - timedelta(hours=12) \
                and datetimenow.time().hour == pump.interval["start_time"].hour \
                and datetimenow.time().minute >= pump.interval["start_time"].minute \
                and datetimenow.time().minute <= pump.interval["start_time"].minute + 1:
                thread = threading.Thread(target=pump.pumpOn, daemon=True)
                thread.start()
            elif (not pump.interval["state"]):
                pump.interval["time_elapsed_since_last_watering"] += timeElapsedIncrement 
                print("pump {} timer: {}".format(pump.interval["index"], pump.interval["time_elapsed_since_last_watering"]))



        
