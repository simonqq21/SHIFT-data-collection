'''
read and print analog values from nine analog soil moisture sensors, pH sensor, and
EC sensor from three ADS1115 i2c ADC modules
convert analog soil moisture sensor values into %, convert pH sensor values into
pH, and EC sensor values into EC (μS/cm).
'''

from time import sleep 
try:
    from hardware.pi_interfaces import i2c 
    from hardware.pi_interfaces import onewires
except:
    pass
try:
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("ads1115 library not present")
try:
    import adafruit_dht
except:
    print("DHT library not present or not running on RPi")
try:
    import adafruit_tca9548a
    import adafruit_bh1750
except:
    print("BH1750 or TCA9548A library not present")

class DHT22():
    def __init__(self, GPIO): # board.D4 or board.D17
        try:
            self.sensor = adafruit_dht.DHT22(GPIO)
        except:
            print("error adding DHT22 on pin {}".format(GPIO))
        self.temperature = 0
        self.humidity = 0 
        self.prevTemperature = 0 
        self.prevHumidity = 0

    def getTemperature(self):
        self.temperature = None
        valid_readings = 0
        total_temp = 0
        for i in range(5):
            try:
                total_temp += self.sensor.temperature
                valid_readings += 1 
            except RuntimeError as err:
                print("runtime error") 
                print(err)
            except OverflowError as err:
                print("overflow error")
                print(err)
            sleep(2)
        if (valid_readings > 0):
            self.temperature = total_temp / valid_readings
            self.prevTemperature = self.temperature
        else:
            self.temperature = self.prevTemperature
        return self.temperature

    def getHumidity(self):
        self.humidity = None
        valid_readings = 0
        total_humd = 0
        for i in range(5):
            try:
                total_humd += self.sensor.humidity
                valid_readings += 1
            except RuntimeError as err:
                print("runtime error") 
                print(err)
            except OverflowError as err:
                print("overflow error")
                print(err)
            sleep(2)
        if (valid_readings > 0):
            self.humidity = total_humd / valid_readings
            self.prevHumidity = self.humidity
        else:
            self.humidity = self.prevHumidity
        return self.humidity

class SoilMoistureSensor:
    def __init__(self, ADSchan, m, b):
        self.type = "soil_moisture"
        self.chan = ADSchan
        self.voltage = None
        self.soilMoisture = None 
        # calibration data 
        self.m = m
        self.b = b

    def getSoilMoisture(self):
        try:
            self.voltage = self.chan.voltage
            self.soilMoisture = self.voltage * self.m + self.b    
            if self.soilMoisture < 0:
                self.soilMoisture = 0 
            elif self.soilMoisture > 1:
                self.soilMoisture = 1
            print(f"sm_voltage = {self.voltage}")
        except:
            print("ADS1115 not connected properly")
        return self.soilMoisture


class PH4502C:
    def __init__(self, ADSchan, m, b):
        self.type = "solution_pH"
        self.chan = ADSchan
        self.voltage = None
        self.pH = None 
        # calibration data 
        self.m = m
        self.b = b

    def getSolutionpH(self):
        try:
            self.voltage = self.chan.voltage
            self.pH = self.voltage * self.m + self.b   
            print(f"ph_voltage = {self.voltage}")
        except:
            print("ADS1115 not connected properly")
        return self.pH


class TDSMeter:
    def __init__(self, ADSchan):
        self.type = "solution_EC"
        self.chan = ADSchan
        self.voltage = None
        self.compensationCoefficient = 0
        self.compensationVoltage = 0 
        self.TDS = 0
        self.EC = 0 

    def getSolutionEC(self, water_temperature):
        self.compensationCoefficient = 1.0 + 0.02 *(water_temperature-25.0)
        try:
            self.voltage = self.chan.voltage
            self.compensationVoltage = self.voltage / self.compensationCoefficient
            self.TDS = (133.42*self.compensationVoltage**3 - 255.86*self.compensationVoltage**2 + 857.39*self.compensationVoltage)*0.5
            self.EC = self.TDS / 500  
        except:
            print("ADS1115 not connected properly")
        return self.EC

class ADS1115:
    def __init__(self, i2c, gain=1, addressIndex=0): # gain=1 to fit the 3v3 range 
        self.gain = gain
        self.address = 72 + addressIndex
        self.chans = []  
        self.sensors = []   
        try:   
            self.ads = ADS.ADS1115(i2c, gain=self.gain, address=self.address)  
            self.chans.append(AnalogIn(self.ads, ADS.P0))
            self.chans.append(AnalogIn(self.ads, ADS.P1))
            self.chans.append(AnalogIn(self.ads, ADS.P2))
            self.chans.append(AnalogIn(self.ads, ADS.P3))
        except Exception as err:
            print(f"Error: {err}")

    def addSoilMoistureSensor(self, m, b):
        if (len(self.sensors) >= 4):
            print("ADS1115 is full, error adding soil moisture sensor")
        else:
            chanIndex = len(self.sensors) - 1 if len(self.sensors) > 0 else 0
            if debug:
                print(chanIndex)
                print(self.chans)
            self.sensors.append(SoilMoistureSensor(self.chans[chanIndex], m, b))

    def addPH4502C(self, m, b):
        if (len(self.sensors) >= 4):
            print("ADS1115 is full, error adding pH sensor")
        else:
            chanIndex = len(self.sensors) - 1 if len(self.sensors) > 0 else 0
            self.sensors.append(PH4502C(self.chans[chanIndex], m, b))

    def addTDSMeter(self):
        if (len(self.sensors) >= 4):
            print("ADS1115 is full, error adding EC sensor")
        else:
            chanIndex = len(self.sensors) - 1 if len(self.sensors) > 0 else 0
            self.sensors.append(TDSMeter(self.chans[chanIndex]))

    def getSoilMoistures(self):
        if debug:
            print("sm")
        soilmoisture_values = []
        for sensor in self.sensors:
            if sensor.type == "soil_moisture":
                if debug:
                    print(sensor.voltage)
                soilmoisture_values.append(sensor.getSoilMoisture())
        if debug:
            print()
        return soilmoisture_values

    def getSolutionpHs(self):
        if debug:
            print("ph")
        solutionpH_values = []
        for sensor in self.sensors:
            if sensor.type == "solution_pH":
                if debug:
                    print(sensor.voltage)
                solutionpH_values.append(sensor.getSolutionpH())
        if debug:
            print()
        return solutionpH_values 

    def getSolutionECs(self, water_temperature=25):
        if debug:
            print("ec")
        solutionEC_values = []
        for sensor in self.sensors:
            if sensor.type == "solution_EC":
                if debug:
                    print(sensor.voltage)
                solutionEC_values.append(sensor.getSolutionEC(water_temperature))
        if debug:
            print()
        return solutionEC_values  

class BH1750:
    def __init__(self, i2c, altAddr=False):
        try:
            if altAddr:
                self.sensor = adafruit_bh1750.BH1750(i2c, address=92)
            else:
                self.sensor = adafruit_bh1750.BH1750(i2c)
        except:
            # print("error adding BH1750 on channel {}".format(i2c))
            exit
        self.lightintensity = None

    def getLightIntensity(self):
        sleep(0.5)
        self.lightintensity = None
        for i in range(5):
            if (self.lightintensity is not None):
                break
            try:
                self.lightintensity = self.sensor.lux
            except Exception as err:
                print(err)
            sleep(0.5) 
        return self.lightintensity

class TCA9548A:
    def __init__(self, i2c, address=112):
        self.bhs = []
        try:
            self.tca = adafruit_tca9548a.TCA9548A(i2c, address=address) 
        except:
            print("error adding TCA9548 on channel {}".format(i2c))
        
    def addBH1750(self, i2cIndex):
        try:
            if (i2cIndex > 7):
                self.bhs.append(BH1750(self.tca[i2cIndex%8], altAddr=True))
            else:
                self.bhs.append(BH1750(self.tca[i2cIndex%8]))
        except Exception as err:
            print(err)
        
    def getLightIntensities(self):
        self.lightIntensities = []
        print(len(self.bhs))
        for bh in self.bhs:
            self.lightIntensities.append(bh.getLightIntensity())
        return self.lightIntensities
