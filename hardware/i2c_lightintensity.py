'''
read and print light intensity values from nine BH1750 sensors connected with the
TCA9548A i2c multiplexer module
'''

from time import sleep
try:
    import board
    import adafruit_tca9548a
    import adafruit_bh1750
except:
    print("BH1750 or TCA9548A library not present")

class BH1750:
    def __init__(self, i2c, altAddr=False):
        try:
            if altAddr:
                self.sensor = adafruit_bh1750.BH1750(i2c, address=92)
            else:
                self.sensor = adafruit_bh1750.BH1750(i2c)
        except:
            print("error adding BH1750 on channel {}".format(i2c))
        self.lightintensity = None

    def update(self):
        sleep(0.5)
        self.lightintensity = None
        for i in range(5):
            if (self.lightintensity is not None):
                break
            try:
                self.lightintensity = self.sensor.lux
            except RuntimeError as err:
                print(err)
            sleep(0.5) 
    
    def getLightIntensity(self):
        return self.lightintensity

class TCA9548A:
    def __init__(self, i2c, address=112):
        self.bhs = []
        try:
            self.tca = adafruit_tca9548a.TCA9548A(i2c, address=address) 
        except:
            print("error adding TCA9548 on channel {}".format(i2c))
        
    def addBH1750(self, i2cIndex):
        if (i2cIndex > 7):
            self.bhs.append(BH1750(self.tca[i2cIndex%8], altAddr=True))
        else:
            self.bhs.append(BH1750(self.tca[i2cIndex%8]))
        
    def getLightIntensities(self):
        self.lightIntensities = []
        print(len(self.bhs))
        for bh in self.bhs:
            bh.update()
            self.lightIntensities.append(bh.getLightIntensity())
        return self.lightIntensities

if __name__ == "__main__":
    bhcount = 9 
    try:
        i2c = board.I2C()
        tca = TCA9548A(i2c)
    except:
        print("Error adding TCA9548")

    for si in range(bhcount):
        try:
            tca.addBH1750(si)
        except Exception as e:
            print(e)
            print("not running on Pi or device not connected properly")

    for i in range(5):
        print(tca.getLightIntensities())
        sleep(2)
# def getLightIntensityValues():
#     lightIntensityReadings = []
#     try:
#         for i in range((len(bhs))):
#             newLightIntensityReading = {} 
#             newLightIntensityReading["index"] = i 
#             newLightIntensityReading["value"] = bhs[i].lux 
#             lightIntensityReadings.append(newLightIntensityReading)
#     except Exception as e:
#         print('BH1750 temperature read error or not running on RPi')
#         print(e)
#         lightIntensityReadings = [] 
#         for i in range((len(bhs))):
#             newLightIntensityReading = {} 
#             newLightIntensityReading["index"] = i 
#             newLightIntensityReading["value"] = -999
#             lightIntensityReadings.append(newLightIntensityReading)
#     return lightIntensityReadings




