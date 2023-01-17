import time

dhts = []
try:
    import adafruit_dht
    import board
    dhts.append(adafruit_dht.DHT22(board.D4))
    dhts.append(adafruit_dht.DHT22(board.D17))
except:
    print("DHT library not present")

'''
get the temperature values from the two DHT22 sensors in °C
'''
def getTemperatureValues(): 
    temperatureReadings = []
    try:
        for i in range(len(dhts)):
            newTemperatureReading = {}
            newTemperatureReading["index"] = i
            newTemperatureReading["value"] = dhts[i].temperature
            temperatureReadings.append(newTemperatureReading)
    except Exception as e:
        print('DHT22 temperature read error or not running on RPi')
        print(e)
        temperatureReadings = []
        for i in range(len(dhts)):
            newTemperatureReading = {}
            newTemperatureReading["index"] = i
            newTemperatureReading["value"] = -100
            temperatureReadings.append(newTemperatureReading)
    return temperatureReadings

'''
get the humidity values from the two DHT22 sensors in %
'''
def getHumidityValues():
    humidityReadings = []
    try:
        for i in range(len(dhts)):
            newHumidityReading = {}
            newHumidityReading["index"] = i
            newHumidityReading["value"] = dhts[i].humidity
            humidityReadings.append(newHumidityReading)
    except Exception as e:
        print('DHT22 humidity read error or not running on RPi')
        print(e)
        humidityReadings = []
        for i in range(len(dhts)):
            newHumidityReading = {}
            newHumidityReading["index"] = i
            newHumidityReading["value"] = -1
            humidityReadings.append(newHumidityReading)
    return humidityReadings


