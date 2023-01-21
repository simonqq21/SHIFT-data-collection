'''
read and print analog values from nine analog soil moisture sensors, pH sensor, and
EC sensor from three ADS1115 i2c ADC modules
convert analog soil moisture sensor values into %, convert pH sensor values into
pH, and EC sensor values into EC (μS/cm).
'''

from time import sleep 
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("ads1115 library not present")

debug = 1 

class SoilMoistureSensor:
    def __init__(self, ADSchan, m, b):
        self.type = "soil_moisture"
        self.chan = ADSchan
        self.voltage = None
        self.soilMoisture = None 
        # calibration data 
        self.m = m
        self.b = b

    def update(self):
        try:
            self.voltage = self.chan.voltage
            self.soilMoisture = self.voltage * self.m + self.b    
        except:
            print("ADS1115 not connected properly")

    def getSoilMoisture(self):
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

    def update(self):
        try:
            self.voltage = self.chan.voltage
            self.pH = self.voltage * self.m + self.b # TODO    
        except:
            print("ADS1115 not connected properly")

    def getSolutionpH(self):
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

    def update(self, water_temperature):
        self.compensationCoefficient = 1.0 + 0.02 *(water_temperature-25.0)
        try:
            self.voltage = self.chan.voltage
            self.compensationVoltage = self.voltage / self.compensationCoefficient
            self.TDS = (133.42*self.compensationVoltage**3 - 255.86*self.compensationVoltage**2 + 857.39*self.compensationVoltage)*0.5
            self.EC = self.TDS / 500  
        except:
            print("ADS1115 not connected properly")

    def getSolutionEC(self):
        return self.EC

class ADS1115:
    def __init__(self, i2c, gain, addressIndex=0):
        self.gain = gain
        self.address = 72 + addressIndex
        self.ads = ADS.ADS1115(i2c, gain=self.gain, address=self.address)  
        self.chans = [] 
        self.chans.append(AnalogIn(self.ads, ADS.P0))
        self.chans.append(AnalogIn(self.ads, ADS.P1))
        self.chans.append(AnalogIn(self.ads, ADS.P2))
        self.chans.append(AnalogIn(self.ads, ADS.P3))
        self.sensors = []  

    def addSoilMoistureSensor(self, m, b):
        if (len(self.sensors) >= 4):
            print("ADS1115 is full, error adding soil moisture sensor")
        else:
            chanIndex = len(self.sensors) - 1 if len(self.sensors) > 0 else 0
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
                sensor.update()
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
                sensor.update()
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
                sensor.update(water_temperature)
                if debug:
                    print(sensor.voltage)
                solutionEC_values.append(sensor.getSolutionEC())
        if debug:
            print()
        return solutionEC_values 

if __name__ == "__main__":
    gain = 2.0/3.0
    try:
        i2c = busio.I2C(board.SCL, board.SDA) 
        adss = []
        adss.append(ADS1115(i2c, gain=gain, addressIndex=0)) # soil moisture sensors 0-3
        adss.append(ADS1115(i2c, gain=gain, addressIndex=1)) # soil moisture sensors 4-7
        adss.append(ADS1115(i2c, gain=gain, addressIndex=2)) # soil moisture sensor 8, pH sensor, and EC sensor

        # add 9 soil moisture sensors throughout three ADS1115 consecutively from channel 0 of ADS1115 index 0
        for i in range(9):
            adss[i//4].addSoilMoistureSensor(m=-0.5, b=0)

        # add 1 pH sensor to channel 1 of ADS1115 index 2
            adss[2].addPH4502C(m=-0.5, b=1)

        # add 1 EC sensor 
            adss[2].addTDSMeter()

    except Exception as e:
        print("ADS1115 not connected or not running on RPi")
        print(e)

    # for i in range(5):
    for ads in adss:
        print(ads.getSoilMoistures())
        print(ads.getSolutionpHs()) 
        print(ads.getSolutionECs())
    sleep(2)
# '''
# get the soil moisture values from the nine soil moisture sensors in %
# '''
# def getSoilMoistureValues():
#     saturation_voltages = [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2] # set to actual saturation values
#     soilMoistureReadings = [] 
#     try:
#         for i in range(9):
#             newSoilMoistureReading = {} 
#             newSoilMoistureReading["index"] = i 
#             newSoilMoistureReading["voltage"] = chans[i].voltage
#             newSoilMoistureReading["value"] = newSoilMoistureReading["voltage"] / saturation_voltages[i]
#             soilMoistureReadings.append(newSoilMoistureReading)
#     except Exception as e: 
#         print("Soil moisture sensor read error or not running on RPi")
#         print(e) 
#         soilMoistureReadings = [] 
#         for i in range(9):
#             newSoilMoistureReading = {} 
#             newSoilMoistureReading["index"] = i 
#             newSoilMoistureReading["voltage"] = -1
#             newSoilMoistureReading["value"] = -1
#             soilMoistureReadings.append(newSoilMoistureReading)
#     return soilMoistureReadings

# '''
# get the pH value from the PH-4502C in pH 
# '''
# def getpHValues():
#     # linear function values for the PH-4502C sensor
#     m = 0 
#     b = 0
#     pHReadings = [] 
#     try:
#         for i in range(9,10):
#             newpHReading = {} 
#             newpHReading["index"] = i 
#             newpHReading["voltage"] = chans[i].voltage
#             newpHReading["value"] = m * newpHReading["voltage"] + b
#             pHReadings.append(newpHReading)
#     except Exception as e: 
#         print("pH sensor read error or not running on RPi")
#         print(e) 
#         pHReadings = [] 
#         for i in range(9,10):
#             newpHReading = {} 
#             newpHReading["index"] = i 
#             newpHReading["voltage"] = -1 
#             newpHReading["value"] = -1
#             pHReadings.append(newpHReading)
#     return pHReadings

# def getECValues(water_temperature): 
#     compensationCoefficient = 1.0 + 0.02 *(water_temperature-25.0)
#     ECReadings = [] 
#     try:
#         for i in range(10,11):
#             newECReading = {} 
#             newECReading["index"] = i 
#             newECReading["voltage"] = chans[i].voltage 
#             compensationVoltage = newECReading["voltage"]/compensationCoefficient
#             TDS = (133.42*compensationVoltage**3 - 255.86*compensationVoltage**2 + 857.39*compensationVoltage)*0.5
#             newECReading["value"] = TDS / 500 
#             ECReadings.append(newECReading)
#     except Exception as e: 
#         print("EC sensor read error or not running on RPi")
#         print(e) 
#         ECReadings = [] 
#         for i in range(10,11):
#             newECReading = {} 
#             newECReading["index"] = i 
#             newECReading["voltage"] = -1
#             newECReading["value"] = -1
#             ECReadings.append(newECReading)
#     return ECReadings 


