'''
read and print analog values from nine analog soil moisture sensors, pH sensor, and
EC sensor from three ADS1115 i2c ADC modules
convert analog soil moisture sensor values into %, convert pH sensor values into
pH, and EC sensor values into EC (μS/cm).
'''

import time
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("ads1115 library not present")

gain = 2.0/3.0
i2c = busio.I2C(board.SCL, board.SDA)
adss = []
adss.append(ADS.ADS1115(i2c, gain=gain))
adss.append(ADS.ADS1115(i2c, gain=gain, address=73))
# adss.append(ADS.ADS1115(i2c, gain=1, address=74))
chans = []
for ads in adss:
    chans.append(AnalogIn(ads, ADS.P0))
    chans.append(AnalogIn(ads, ADS.P1))
    chans.append(AnalogIn(ads, ADS.P2))
    chans.append(AnalogIn(ads, ADS.P3))

values = [0]*len(chans)
voltages = [0]*len(chans)
while True:
    for i in range(len(chans)):
        values[i] = chans[i].value
        voltages[i] = chans[i].voltage

    for i in range(len(chans)):
        print("value[{}]={}, voltage[{}]={}".format(i, values[i], i, voltages[i]))
    print()
    time.sleep(3)
