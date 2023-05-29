from time import sleep
import json
from datetime import datetime, date, time, timedelta
import threading
from io import BytesIO
try:
    from picamera import PiCamera
    from gpiozero import DigitalOutputDevice, Button
except Exception as e:
    print("picamera or gpiozero library not present")
    print("Exception = ")
    print(e)
import os 
import binascii

