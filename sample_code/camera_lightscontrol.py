'''
capture and save an 8 MP image from the Raspberry Pi Camera v2
temporarily switch off the purple LED grow lights and switch on the white LED lights
when taking the picture
'''

import time
try:
    from picamera import PiCamera
    from gpiozero import DigitalOutputDevice
except:
    print("picamera or gpiozero library not present")

try:
    camera = PiCamera()
    camera.resolution = (3280, 2464)
    print(camera)
except:
    print("Failed to create camera object!")

growlight = DigitalOutputDevice(18)
cameralight = DigitalOutputDevice(27)
growlight.on()
time.sleep(5)
growlight.off()
cameralight.on()
camera.capture()
