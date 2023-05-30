try:
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.lights import Lights
    import socket
except Exception as e:
    print(e)
from config import Config

HOST = "localhost"
PORT = 12003

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.bind((HOST, PORT)) 
client.listen()

lights = Lights() 

while True:
    communication_socket, address = client.accept() 
    print(f"Connected to {address}")
    message = communication_socket.recv(1024)
    print(type(message))
    message = message.decode('utf-8')
    commandType = message.split()[0]
    if commandType == "lights":
        lightType = message.split()[1]
        if lightType == 'p': # purple grow light
            onTime = int(message.split()[2])
            lights.growLightOn(onTime)
        elif lightType == 'w': # white camera light 
            onTime = int(message.split()[2])
            lights.cameraLightOn(onTime)
        elif lightType == 'flash': # flash the white camera light 
            lights.flashCameraLight()
        # set light states below this line 
            
    # communication_socket.close() 

'''
lights p 43200
lights w 4

lights <light type> <time on in seconds>
light type - p for purple or w for white 
time on in seconds - positive for timer, 0 for off, and negative for on 

lights flash
lights <camera_flash>
camera_flash - save state of grow lamps, shut down grow lamps, 
turn on white camera lights for 4 secs, turns off white camera lights,
then restores state of grow lamps.
'''