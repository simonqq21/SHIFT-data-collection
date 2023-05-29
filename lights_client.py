try:
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.growlights_camera import LightsCamera
    import socket
except Exception as e:
    print(e)
from config import Config

'''
lights purple on
lights purple off
lights white on
lights white off 
lights white flash 

00
first bit - grow lights
second bit - white lights
'''