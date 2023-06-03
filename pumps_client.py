try:
    import socket
    import json
    import os
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.pumps import PumpSystem
    import socket
except Exception as e:
    print(e)
from config import Config

class PumpsClient():
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 12002
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((self.HOST, self.PORT)) 
        self.client.listen()
        self.pumps = PumpSystem() 

    def loop(self):
        while True:
            self.communication_socket, self.address = self.client.accept() 
            print(f"Connected to {self.address}")
            message = self.communication_socket.recv(1024)
            # print(type(message))
            message = message.decode('utf-8')
            commandType = message.split()[0]
            if commandType == "pumps":
                pumpIndex = int(message.split()[1]) 
                duration = int(message.split()[2]) 
                # set pump states below this line 
                pumpOnThread = threading.Thread(target=self.pumps.switchOn, args=(pumpIndex, duration))
                pumpOnThread.start()
                
                # print(f"Message from server is: {message}")
                # self.communication_socket.send(f"self.client 1 response!".encode('utf-8'))
                # self.communication_socket.close() 
'''
pumps 1 10
pumps 2 10
pumps 3 10

pumps <pump index> <time on in seconds>
pump index - one-indexed 
time on in seconds - positive for timer, 0 for off 
'''

if __name__ == "__main__":
    pumpsclient = PumpsClient()
    pumpsclient.loop()