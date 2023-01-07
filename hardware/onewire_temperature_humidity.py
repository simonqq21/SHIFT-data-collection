import time
import board
try:
    import adafruit_dht
except:
    print("DHT library not present")

dhts = []
print(board)
dhts.append(adafruit_dht.DHT22(board.D4))
dhts.append(adafruit_dht.DHT22(board.D17))


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
        for temperatureReading in temperatureReadings:
            temperatureReading["index"] = i
            temperatureReading["value"] = -100
    return temperatureReadings

def getHumidityValues():
    humidityReadings = []
    try:
        for i in range(len(dhts)):
            newHumidityReading = {}
            newHumidityReading["index"] = i
            newHumidityReading["value"] = dhts[i].humidity
            humidityReadings.append(newHumidityReading)
    except Exception as e:
        print('DHT22 humidity read error ')
        print(e)
        for humidityReading in humidityReadings:
            humidityReading["index"] = i
            humidityReading["value"] = -1
    return humidityReadings


