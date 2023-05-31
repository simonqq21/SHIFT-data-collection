try:
    import json
    import os
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    import numpy as np
    import pandas as pd

    import socket 
    from _thread import * 
    
except Exception as e:
    print(e)
from config import Config

class SyncServer(): 
    def __init__(self):
        self.HOST = "localhost"
        # last date when the datetimes for the camera and sensors were generated
        self.lastUpdateDate = date(year=1970, month=1, day=1)
        # used for timing
        self.intervalLastChecked = datetime(year=1970, month=1, day=1)
        self.sensorsLastPolled = datetime(year=1970, month=1, day=1)
     
    def connect(self, server, HOST, PORT, retries=8, timeout_per_retry=5):
        for i in range(retries):
            try:
                server.connect((HOST, PORT))
                return 1
            except ConnectionRefusedError as err:
                print("connection failed, retrying. ")
                sleep(timeout_per_retry) 
        print("Connection timed out.")
        return 0 

    def pumpsControl(self, pumpIndex, duration): 
        PORT = 12002
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = f"pumps {pumpIndex} {duration}"
        if status:
            server.send(command.encode('utf-8')) 
            print("sent pumps command") 

    def lightsControl(self, lightType = "purple", duration=0):
        PORT = 12003
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = "lights " + str(purpleState) + str(whiteState)
        if status:
            server.send(command.encode('utf-8')) 
            print("sent lights command")
            # print(server.recv(1024)) 

    def cameraCapture(self): 
        PORT = 12004
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = "camera"
        if status:
            server.send(command.encode('utf-8'))  
            print("sent camera command")

    def sensorsLog(self): 
        PORT = 12005
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT) 
        command = "sensors"
        if status:
            server.send(command.encode('utf-8')) 
            print("sent sensors command") 

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
        
    def loop(self):
        # for timekeeping
        # self.datetimenow = datetime.combine(date.today(), time(hour=7, minute=0, second=0))
        self.datetimenow = datetime.now()
        while True:
            # update the growLightIntervals and cameraIntervals with the times of the day 
            if (date.today() > self.lastUpdateDate):
                # self.datetimenow = datetime.now()
                self.lastUpdateDate = date.today() 
                self.lightscamera.getGrowLightIntervalsPerDay()
                self.lightscamera.getCameraIntervalsPerDay()
                
            # loop to check the camera, growlights, and pump
            if (datetime.now() - self.intervalLastChecked >= Config.checkingInterval):
                self.intervalLastChecked = datetime.now()
                # loop to check switch grow lights
                self.lightscamera.pollGrowLights(self.datetimenow)
                print("val={}".format(self.lightscamera.growlightval))
                '''
                while the camera is capturing an image, the growlight code must be overriden.
                '''
                # loop to capture image 
                self.lightscamera.pollCamera(self.datetimenow)
                self.publishNewImage()

                # loop to check and run irrigation pumps
                self.pumps.pollPumps(self.datetimenow)
            # loop to gather sensor data from all sensors, package it into json, and send it via MQTT 
            if (self.datetimenow - self.sensorsLastPolled >= Config.sensorPollingInterval and \
                self.datetimenow >= datetime.combine(self.datetimenow.date(), Config.sensor_logging_start) and \
                self.datetimenow <= datetime.combine(self.datetimenow.date(), Config.sensor_logging_end)):
                self.sensorsLastPolled = datetime.now()
                self.captureSensors()
            sleep(1)
