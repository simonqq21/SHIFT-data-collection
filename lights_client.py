try:
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.lights import Lights
    import socket
except Exception as e:
    print(e)
from config import Config

class LightsClient():
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 12003
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((self.HOST, self.PORT)) 
        self.client.listen()
        self.lights = Lights() 

    def loop(self):
        while True:
            self.communication_socket, self.address = self.client.accept() 
            print(f"Connected to {self.address}")
            message = self.communication_socket.recv(1024)
            print(type(message))
            message = message.decode('utf-8')
            commandType = message.split()[0]
            if commandType == "lights":
                lightType = message.split()[1]
                if lightType == 'p': # purple grow light
                    onTime = int(message.split()[2])
                    growLightThread = threading.Thread(target=self.lights.growLightOn, args=(onTime,))
                    growLightThread.start()
                elif lightType == 'w': # white camera light 
                    print(type(message.split()[2]))
                    onTime = int(message.split()[2])
                    whiteLightThread = threading.Thread(target=self.lights.cameraLightOn, args=(onTime,))
                    whiteLightThread.start()
                elif lightType == 'flash': # flash the white camera light 
                    cameraFlashThread = threading.Thread(target=self.lights.flashCameraLight)
                    cameraFlashThread.start()
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

if __name__ == "__main__":
    lightsclient = LightsClient()
    lightsclient.loop()