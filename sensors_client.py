try:
    import socket
    import json
    import os
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    import socket
    import numpy as np
    import paho.mqtt.client as mqtt
    import pandas as pd
    from hardware.sensors import Sensors
except Exception as e:
    print(e)
from config import Config

class SensorClient():
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 12005
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((self.HOST, self.PORT)) 
        self.client.listen()
        self.sensors = Sensors() 

    def loop(self):
        while True:
            self.communication_socket, self.address = self.client.accept() 
            print(f"Connected to {self.address}")
            message = self.communication_socket.recv(1024)
            print(type(message))
            message = message.decode('utf-8')
            commandType = message.split()[0]
            if commandType == "sensors":
                # log sensor data 
                command = message.split()[1]
                if command == "capture":
                    print("logging sensor data")
                    sensorLoggingThread = threading.Thread(target=self.sensors.captureSensors)
                    sensorLoggingThread.start() 
            
    # print(f"Message from client is: {message}")
    # communication_socket.send(f"client 2 response!".encode('utf-8'))
    # communication_socket.close() 
'''
sensors capture 
- log all environmental sensors, save it to CSV file, and publish it on MQTT broker
'''