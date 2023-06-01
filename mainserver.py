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
        
        '''
        Camera and sensors are periodic with a start and end time, while 
        pumps and lights are periodic with defined opening and closing times.
        '''

        # used for timing periodic events such as the cameras and sensors
        self.timeLastSensorsLogged = datetime(year=1970, month=1, day=1)      
        self.timeLastCameraCaptured = datetime(year=1970, month=1, day=1)



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
            if Config.debug:
                print("sent pumps command") 
    '''
    lightType is either 'p', 'w', or 'flash'
    '''
    def lightsControl(self, lightType = "p", duration=timedelta(seconds=5)):
        PORT = 12003
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        duration = duration.total_seconds()
        if lightType == 'flash':
            command = "lights flash"
        else:    
            command = f"lights {lightType} {duration}"
        if status:
            server.send(command.encode('utf-8')) 
            if Config.debug:
                print("sent lights command")
            # print(server.recv(1024)) 

    def cameraCapture(self): 
        PORT = 12004
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = "camera capture"
        if status:
            server.send(command.encode('utf-8'))  
            if Config.debug:
                print("sent camera command")

    def sensorsLog(self): 
        PORT = 12005
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT) 
        command = "sensors capture"
        if status:
            server.send(command.encode('utf-8')) 
            if Config.debug:
                print("sent sensors command")    

    def loop(self):
        # for timekeeping
        # self.datetimenow = datetime.combine(date.today(), time(hour=7, minute=0, second=0))

        while True:
            self.datetimenow = datetime.now()
            timeNow = self.datetimenow.time
            # tell the sensors module to capture and transmit sensor data
            '''
            if the current time is in between the start and end times for sensor logging and if the 
            time since last sensor logging has exceeded the set sensor logging interval  
            '''
            if (self.datetimenow - self.timeLastSensorsLogged >= Config.sensorLoggingInterval and \
                self.datetimenow >= datetime.combine(self.datetimenow.date(), Config.sensor_logging_start) and \
                self.datetimenow <= datetime.combine(self.datetimenow.date(), Config.sensor_logging_end)): 
                self.timeLastSensorsLogged = self.datetimenow
                self.sensorsLog()

            # tell the camera module to capture and transmit image data
            '''
            if the current time is in between the start and end times for camera capture and if the 
            time since last camera capture has exceeded the set camera capture interval  
            '''
            if (self.datetimenow - self.timeLastCameraCaptured >= Config.cameraCaptureInterval and \
                self.datetimenow >= datetime.combine(self.datetimenow.date(), Config.camera_capture_start) and \
                self.datetimenow <= datetime.combine(self.datetimenow.date(), Config.camera_capture_end)): 
                self.timeLastCameraCaptured = self.datetimenow
                # flash the white light and capture an image 
                self.lightsControl("flash")
                self.cameraCapture()

            # tell the pumps module to turn the pumps on for a certain duration
            '''
            iterate through each 
            '''
            if (self.datetimenow - self.timeLastCameraCaptured >= Config.cameraCaptureInterval and \
                self.datetimenow >= datetime.combine(self.datetimenow.date(), Config.camera_capture_start) and \
                self.datetimenow <= datetime.combine(self.datetimenow.date(), Config.camera_capture_end)): 
                self.timeLastCameraCaptured = self.datetimenow
                self.cameraCapture()

            # tell the lights module to turn on the lights to the correct mode
  

              
            # # loop to check the camera, growlights, and pump
            # if (datetime.now() - self.intervalLastChecked >= Config.checkingInterval):
            #     self.intervalLastChecked = datetime.now()
            #     # loop to check switch grow lights
            #     self.lightscamera.pollGrowLights(self.datetimenow)
            #     print("val={}".format(self.lightscamera.growlightval))
            #     '''
            #     while the camera is capturing an image, the growlight code must be overriden.
            #     '''
            #     # loop to capture image 
            #     self.lightscamera.pollCamera(self.datetimenow)
            #     self.publishNewImage()

            #     # loop to check and run irrigation pumps
            #     self.pumps.pollPumps(self.datetimenow)
            # # loop to gather sensor data from all sensors, package it into json, and send it via MQTT 
            #     self.sensorsLastPolled = datetime.now()
            #     self.captureSensors()
            # sleep(1)
