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

HOST = "localhost"
PORT = 12005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.bind((HOST, PORT)) 
client.listen()

sensors = Sensors() 

while True:
    communication_socket, address = client.accept() 
    print(f"Connected to {address}")
    message = communication_socket.recv(1024)
    print(type(message))
    message = message.decode('utf-8')
    commandType = message.split()[0]
    if commandType == "sensors":
        # log sensor data 
        command = message.split()[1]
        if command == "capture":
            print("logging sensor data")
            sensorLoggingThread = threading.Thread(target=sensors.captureSensors)
            sensorLoggingThread.start() 
            
    # print(f"Message from client is: {message}")
    # communication_socket.send(f"client 2 response!".encode('utf-8'))
    # communication_socket.close() 
'''
sensors capture 
- log all environmental sensors, save it to CSV file, and publish it on MQTT broker
'''