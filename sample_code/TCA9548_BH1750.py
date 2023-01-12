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
try:
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c, address=112)
except:
    print("Error adding TCA9548")
bhs = []
for si in range(bhcount):
    try:
        if (si > 7):
            bhs.append(adafruit_bh1750.BH1750(tca[si%8], address=92))
        else:
            bhs.append(adafruit_bh1750.BH1750(tca[si%8]))
    except Exception as e:
        print(e)
        print("not running on Pi or device not connected properly")
        pass

luxs = [0]*bhcount
print(len(bhs))
while True:

    for i in range((len(bhs))):
        luxs[i] = bhs[i].lux

    for i in range((len(bhs))):
        print("lux[{}]={}".format(i, luxs[i]))
    
    print()
    time.sleep(3)
