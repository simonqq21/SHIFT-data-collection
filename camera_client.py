try:
    import socket
    import json
    import os
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.camera import Camera
    import socket
except Exception as e:
    print(e)
from config import Config
from email_sender import emailExited, emailCrashed
import atexit

class CameraClient():
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 12004
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((self.HOST, self.PORT)) 
        self.client.listen()
        self.camera = Camera() 
    
    def loop(self):
        while True:
            self.communication_socket, self.address = self.client.accept() 
            print(f"Connected to {self.address}")
            message = self.communication_socket.recv(1024)
            print(type(message))
            message = message.decode('utf-8')
            commandType = message.split()[0]
            if commandType == "camera":
                # capture image with camera  
                command = message.split()[1]
                if command == "capture":
                    print("capturing and transmitting image")
                    cameraCaptureThread = threading.Thread(target=self.camera.captureImage) 
                    cameraCaptureThread.start() 
                    
    # print(f"Message from client is: {message}")
    # communication_socket.send(f"client 2 response!".encode('utf-8'))
    # communication_socket.close() 

'''
camera capture
- capture an image, save it to internal storage, and publish it on MQTT broker
'''

if __name__ == "__main__":
    datetimenow = datetime.now()
    name = "PGMS camera client"
    try:
        cameraclient = CameraClient()
        atexit.register(emailExited, name, datetimenow)
        cameraclient.loop()
    except Exception as e:
        if Config.debug:
            print(f"{name} crashed")
            print(f"exception={e}")
        emailCrashed(name, datetimenow, e)
