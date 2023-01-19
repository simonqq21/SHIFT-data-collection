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

class SoilMoistureSensor:
    def __init__(self, ADSchan):
        self.chan = ADSchan
        self.voltage = None
        self.soilMoisture = None 

    def update(self):
        try:
            self.voltage = self.chan.voltage
            self.soilMoisture = self.voltage # TODO    
        except:
            print("ADS1115 not connected properly")

    def getSoilMoisture(self):
        return self.soilMoisture
    

class PH4502C:
    def __init__(self, ADSchan):
        self.chan = ADSchan
        self.voltage = None
        self.soilMoisture = None 

    def update(self):
        try:
            self.voltage = self.chan.voltage
            self.soilMoisture = self.voltage # TODO    
        except:
            print("ADS1115 not connected properly")

    def getSoilMoisture(self):
        return self.soilMoisture


class TDSMeter:

    def __init__(self, ADSchan):
        self.chan = ADSchan
        self.voltage = None
        self.compensationCoefficient = 0
        self.compensationVoltage = 0 
        self.TDS = 0
        self.EC = 0 

    def update(self, temperature, ):
        self.compensationCoefficient = 1.0 + 0.02 *(temperature-25.0)
        try:
            self.voltage = self.chan.voltage
            self.compensationVoltage = self.voltage / self.compensationCoefficient
            self.TDS = (133.42*self.compensationVoltage**3 - 255.86*self.compensationVoltage**2 + 857.39*self.compensationVoltage)*0.5
            self.EC = self.TDS / 500  
        except:
            print("ADS1115 not connected properly")

    def getEC(self):
        return self.EC


class ADS1115:
    def __init__(self, address):
        self.chan = ADSsensor

class ADS1115Array:


gain = 2.0/3.0
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    adss = []
    adss.append(ADS.ADS1115(i2c, gain=gain)) # soil moisture sensors 0-3
    adss.append(ADS.ADS1115(i2c, gain=gain, address=73)) # soil moisture sensors 4-7
    adss.append(ADS.ADS1115(i2c, gain=1, address=74)) # soil moisture sensor 8, pH sensor, and EC sensor
    chans = []
    '''
    chans[0:9] - soil moisture sensors 1-9 
    chans[9] - pH sensor 
    chans[10] - EC sensor
    '''
    for ads in adss:
        chans.append(AnalogIn(ads, ADS.P0))
        chans.append(AnalogIn(ads, ADS.P1))
        chans.append(AnalogIn(ads, ADS.P2))
        chans.append(AnalogIn(ads, ADS.P3))
except:
    print("ADS1115 not connected or not running on RPi")

'''
get the soil moisture values from the nine soil moisture sensors in %
'''
def getSoilMoistureValues():
    saturation_voltages = [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2] # set to actual saturation values
    soilMoistureReadings = [] 
    try:
        for i in range(9):
            newSoilMoistureReading = {} 
            newSoilMoistureReading["index"] = i 
            newSoilMoistureReading["voltage"] = chans[i].voltage
            newSoilMoistureReading["value"] = newSoilMoistureReading["voltage"] / saturation_voltages[i]
            soilMoistureReadings.append(newSoilMoistureReading)
    except Exception as e: 
        print("Soil moisture sensor read error or not running on RPi")
        print(e) 
        soilMoistureReadings = [] 
        for i in range(9):
            newSoilMoistureReading = {} 
            newSoilMoistureReading["index"] = i 
            newSoilMoistureReading["voltage"] = -1
            newSoilMoistureReading["value"] = -1
            soilMoistureReadings.append(newSoilMoistureReading)
    return soilMoistureReadings

'''
get the pH value from the PH-4502C in pH 
'''
def getpHValues():
    # linear function values for the PH-4502C sensor
    m = 0 
    b = 0
    pHReadings = [] 
    try:
        for i in range(9,10):
            newpHReading = {} 
            newpHReading["index"] = i 
            newpHReading["voltage"] = chans[i].voltage
            newpHReading["value"] = m * newpHReading["voltage"] + b
            pHReadings.append(newpHReading)
    except Exception as e: 
        print("pH sensor read error or not running on RPi")
        print(e) 
        pHReadings = [] 
        for i in range(9,10):
            newpHReading = {} 
            newpHReading["index"] = i 
            newpHReading["voltage"] = -1 
            newpHReading["value"] = -1
            pHReadings.append(newpHReading)
    return pHReadings

def getECValues(temperature): 
    compensationCoefficient = 1.0 + 0.02 *(temperature-25.0)
    ECReadings = [] 
    try:
        for i in range(10,11):
            newECReading = {} 
            newECReading["index"] = i 
            newECReading["voltage"] = chans[i].voltage 
            compensationVoltage = newECReading["voltage"]/compensationCoefficient
            TDS = (133.42*compensationVoltage**3 - 255.86*compensationVoltage**2 + 857.39*compensationVoltage)*0.5
            newECReading["value"] = TDS / 500 
            ECReadings.append(newECReading)
    except Exception as e: 
        print("EC sensor read error or not running on RPi")
        print(e) 
        ECReadings = [] 
        for i in range(10,11):
            newECReading = {} 
            newECReading["index"] = i 
            newECReading["voltage"] = -1
            newECReading["value"] = -1
            ECReadings.append(newECReading)
    return ECReadings 


