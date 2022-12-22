'''
read and print light intensity values from nine BH1750 sensors connected with the
TCA9548A i2c multiplexer module
'''

import time
try:
    import board
    import adafruit_tca9548a
    import adafruit_bh1750
except:
    print("BH1750 or TCA9548A library not present")

bhcount = 9
i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
bhs = []
for si in range(bhcount):
    if (si > 7):
        bhs.append(adafruit_bh1750.BH1750(tca[si%8], address=92))
    else
        bhs.append(adafruit_bh1750.BH1750(tca[si%8]))

luxs = [0]*bhcount
while True:
    for i in range(bhcount):
        luxs[i] = bhs[i].lux

    for i in range(bhcount):
        print("lux[{i}]={luxval}".format(i, luxs[i]))
    time.sleep(3000)
