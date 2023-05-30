try:
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.lights import Lights
    import socket
except Exception as e:
    print(e)
from config import Config

'''
p 43200
w 4

<light type> <time on in seconds>
light type - p for purple or w for white 
time on in seconds - positive for timer, 0 for off, and negative for on 

c
<camera_flash>
camera_flash - save state of grow lamps, shut down grow lamps, 
turn on white camera lights for 4 secs, turns off white camera lights,
then restores state of grow lamps.
'''