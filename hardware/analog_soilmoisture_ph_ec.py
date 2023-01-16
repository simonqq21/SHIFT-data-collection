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
            newSoilMoistureReading["soilmoisture_value"] = newSoilMoistureReading["voltage"] / saturation_voltages[i]
            soilMoistureReadings.append(newSoilMoistureReading)
    except Exception as e: 
        print("Soil moisture sensor read error or not running on RPi")
        print(e) 
        soilMoistureReadings = [] 
        for i in range(9):
            newSoilMoistureReading = {} 
            newSoilMoistureReading["index"] = i 
            newSoilMoistureReading["voltage"] = -1
            newSoilMoistureReading["soilmoisture"] = -1
            soilMoistureReadings.append(newSoilMoistureReading)
    return soilMoistureReadings

'''
get the pH value from the PH-4502C in pH 
'''
def getpHValue():
    # linear function values for the PH-4502C sensor
    m = 0 
    b = 0
    pHReadings = [] 
    try:
        for i in range(9,10):
            newpHReading = {} 
            newpHReading["index"] = i 
            newpHReading["voltage"] = chans[i].voltage
            newpHReading["pH_value"] = m * newpHReading["voltage"] + b
            pHReadings.append(newpHReading)
    except Exception as e: 
        print("pH sensor read error or not running on RPi")
        print(e) 
        pHReadings = [] 
        for i in range(9,10):
            newpHReading = {} 
            newpHReading["index"] = i 
            newpHReading["voltage"] = -1 
            newpHReading["pH_value"] = -1
            pHReadings.append(newpHReading)
    return pHReadings

def getECValue(temperature): 
    compensationCoefficient = 1.0 + 0.02 *(temperature-25.0)
    ECReadings = [] 
    try:
        for i in range(10,11):
            newECReading = {} 
            newECReading["index"] = i 
            newECReading["voltage"] = chans[i].voltage 
            compensationVoltage = newECReading["voltage"]/compensationCoefficient
            newECReading["TDS_value"] = (133.42*compensationVoltage**3 - 255.86*compensationVoltage**2 + 857.39*compensationVoltage)*0.5
            newECReading["EC_value"] = newECReading["TDS_value"] / 500 
            ECReadings.append(newECReading)
    except Exception as e: 
        print("EC sensor read error or not running on RPi")
        print(e) 
        ECReadings = [] 
        for i in range(10,11):
            newECReading = {} 
            newECReading["index"] = i 
            newECReading["voltage"] = -1
            newECReading["TDS_value"] = -1
            newECReading["EC_value"] = -1
            ECReadings.append(newECReading)
    return ECReadings 


