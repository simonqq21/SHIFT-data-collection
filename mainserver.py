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

        # store the number of times each pump was switched on for the day
        self.pumpsOnCount = [0, 0, 0]  # three pumps

        # flag that is True whenever the camera is capturing an image
        '''
        this is checked by the sensor logging code so that the light intensity sensors
        do not capture readings when the white camera light is on 
        '''
        self.whiteLightOn = False

        self.datetimenow = datetime.now()


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

    def pumpsThreadLoop(self):        
        # initialize datetime
        pumpsDateTime = datetime.now()
        timeOffset = datetime.now() - pumpsDateTime # offset timedelta 

        '''
        generate pump schedule completion array
        0 if not done yet, 1 if done 
        '''
        def createPumpSchedules():
            pumpsSchedulesDoneList = []
            # for each pump in pumps
            for i in range(len(Config.pumps_start_duration)): 
                newPump = []
                # for each schedule in pump
                for j in range(len(Config.pumps_start_duration[i])):
                    newPump.append(0) 
                pumpsSchedulesDoneList.append(newPump)
            if Config.debug:
                print(pumpsSchedulesDoneList)
            return pumpsSchedulesDoneList 
        
        def resetPumpSchedules(pumpsSchedulesDoneList):
            # for each pump in pumps
            for pumpSchedules in pumpsSchedulesDoneList:
                # for each schedule in pump
                for schedule in pumpSchedules:
                    schedule = 0
            if Config.debug:
                print("Reset pump schedules done list")
            return pumpsSchedulesDoneList

        def checkAllZeroes(pumpsSchedulesDoneList):
            # for each pump in pumps
            for pumpSchedules in pumpsSchedulesDoneList:
                # for each schedule in pump
                for schedule in pumpSchedules:
                    if schedule !=0:
                        return False
            return True

        pumpsSchedulesDoneList = createPumpSchedules()
        while True:
            timeNow = pumpsDateTime.time()
            dateNow = pumpsDateTime.date()
            # code to run at the start of each day
            dayStart = time(hour=0, minute=0, second=0)
            if (timeNow >= dayStart and timeNow <= dayStart + timedelta(seconds=59)):
                # reset pumps schedules done list each start of the day 
                if (not checkAllZeroes(pumpsSchedulesDoneList)):
                    pumpsSchedulesDoneList = resetPumpSchedules(pumpsSchedulesDoneList)
                    if Config.debug:
                        print("new day")

            
            for pumpIndex in range(len(Config.pumps_start_duration)):
                currentPump = Config.pumps_start_duration[pumpIndex]
                for scheduleIndex in range(len(currentPump)):
                    (start, duration) = currentPump[scheduleIndex] 
                    if (pumpsDateTime >= datetime.combine(dateNow, start) and \
                        pumpsDateTime <= datetime.combine(dateNow, start + timedelta(seconds=59)) and \
                        pumpsSchedulesDoneList[pumpIndex][scheduleIndex] == 0):
                        pumpsSchedulesDoneList[pumpIndex][scheduleIndex] = 1
                        pumpOnThread = threading.Thread(target=self.pumpsControl, args=(pumpIndex, duration))
                        pumpOnThread.start()
                        if Config.debug:
                            print(f"sent pump {pumpIndex} start command")
            pumpsDateTime = datetime.now() - timeOffset

    '''
    lightType is either 'p', 'w', or 'flash'
    '''
    def lightsControl(self, lightType="p", duration=timedelta(seconds=5)):
        PORT = 12003
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        duration = duration.total_seconds()
        if lightType == 'flash':
            command = "lights flash"
            self.whiteLightOn = True
        else:
            command = f"lights {lightType} {duration}"
        if lightType == 'w':
            self.whiteLightOn = True
        if status:
            server.send(command.encode('utf-8'))
            if Config.debug:
                print("sent lights command")
            # print(server.recv(1024))

    def lightsThreadLoop(self):
        lightsDateTime = self.datetimenow
        while True:
            timeNow = self.datetimenow.time()
            dateNow = self.datetimenow.date()
            # code to run at the start of each day
            if (self.datetimenow.time() >= time(hour=0, minute=0, second=0) and \
                    self.datetimenow.time() <= time(hour=0, minute=0, second=59)):
                if Config.debug:
                    print("new day")
                # insert code to run at the start of each day
            
            self.datetimenow += 1
        
                        # tell the lights module to turn on the grow lights to the correct mode
            for (start, duration) in Config.growlights_on_times_durations:
                if (self.datetimenow >= datetime.combine(self.datetimenow.date(), start) and \
                        self.datetimenow <= datetime.combine(self.datetimenow.date(), \
                                                             start + duration)):
                    duration = datetime.combine(self.datetimenow.date(), start) + duration - self.datetimenow
                    growLightsOnThread = threading.Thread(target=self.lightsControl, args=('p', duration))
                    growLightsOnThread.start() 
                    if Config.debug:
                        print("sent growlights on command") 


    def cameraCapture(self):
        PORT = 12004
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = "camera capture"
        time.sleep(2)
        if status:
            server.send(command.encode('utf-8'))
            if Config.debug:
                print("sent camera command")
        time.sleep(5)
        self.whiteLightOn = False

    def cameraThreadLoop(self):
        cameraDateTime = self.datetimenow
        while True:
            timeNow = cameraDateTime.time()
            dateNow = cameraDateTime.date()
            # code to run at the start of each day
            if (self.datetimenow.time() >= time(hour=0, minute=0, second=0) and \
                    self.datetimenow.time() <= time(hour=0, minute=0, second=59)):
                if Config.debug:
                    print("new day")
                # insert code to run at the start of each day

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
                cameraLightThread = threading.Thread(target=self.lightsControl, args=("flash,"))
                cameraLightThread.start()
                # capture the image
                cameraCaptureThread = threading.Thread(target=self.cameraCapture)
                cameraCaptureThread.start()


    def sensorsLog(self):
        PORT = 12005
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        status = self.connect(server, self.HOST, PORT)
        command = "sensors capture"
        # do not capture light intensity readings when the white camera light is on
        while self.whiteLightOn:
            sleep(0.5)
            if Config.debug:
                print("sensors waiting for white light to turn off")
        if status:
            server.send(command.encode('utf-8'))
            if Config.debug:
                print("sent sensors command")

    def sensorsThreadLoop(self):
        while True:
            
            timeNow = self.datetimenow.time()
            dateNow = self.datetimenow.date()
            # code to run at the start of each day
            if (self.datetimenow.time() >= time(hour=0, minute=0, second=0) and \
                    self.datetimenow.time() <= time(hour=0, minute=0, second=59)):
                if Config.debug:
                    print("new day")
                # insert code to run at the start of each day

            # tell the sensors module to capture and transmit sensor data
            '''
            if the current time is in between the start and end times for sensor logging and if the 
            time since last sensor logging has exceeded the set sensor logging interval  
            '''
            if (self.datetimenow - self.timeLastSensorsLogged >= Config.sensorLoggingInterval and \
                self.datetimenow >= datetime.combine(self.datetimenow.date(), Config.sensor_logging_start) and \
                    self.datetimenow <= datetime.combine(self.datetimenow.date(), Config.sensor_logging_end)):
                self.timeLastSensorsLogged = self.datetimenow
                # start the sensor logging thread
                sensorThread = threading.Thread(target=self.sensorsLog)
                sensorThread.start()


    def loop(self):
        # self.datetimenow = datetime.combine(date.today(), time(hour=7, minute=0, second=0))
        pumpsThread = threading.Thread(target=self.pumpsThreadLoop) 
        pumpsThread.start() 
        lightsThread = threading.Thread(target=self.lightsThreadLoop) 
        lightsThread.start() 
        sensorsThread = threading.Thread(target=self.sensorsThreadLoop)
        sensorsThread.start()
        cameraThreadLoop = threading.Thread(target=self.cameraThreadLoop)
        cameraThreadLoop.start()

if __name__ == "__main__":
    syncserver = SyncServer()
    syncserver.loop()