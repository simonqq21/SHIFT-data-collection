import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

gain = 1

i2c = busio.I2C(board.SCL, board.SDA)
adss = []
adss.append(ADS.ADS1115(i2c))
adss.append(ADS.ADS1115(i2c, address=73))
adss.append(ADS.ADS1115(i2c, address=74))
chans = []
for ads in adss:
    chans.append(AnalogIn(ads, ADS.P0))
    chans.append(AnalogIn(ads, ADS.P1))
    chans.append(AnalogIn(ads, ADS.P2))
    chans.append(AnalogIn(ads, ADS.P3))

while True:
    
