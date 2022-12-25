'''
switch on the pumps at different intervals
'''

import time
try:
    from gpiozero import DigitalOutputDevice
except:
    print("gpiozero library not present")

pumps = []
pumps.append(DigitalOutputDevice(22))
pumps.append(DigitalOutputDevice(23))
pumps.append(DigitalOutputDevice(24))
