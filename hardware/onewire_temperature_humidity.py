from time import sleep
try:
    import adafruit_dht
    import board
except:
    print("DHT library not present or not running on RPi")

class DHT22():
    def __init__(self, GPIO): # board.D4 or board.D17
        try:
            self.sensor = adafruit_dht.DHT22(GPIO)
        except:
            print("error adding DHT sensor on pin {}".format(GPIO))
        self.temperature = None
        self.humidity = None 

    def update(self):
        self.temperature = None
        self.humidity = None
        sleep(3)
        while (self.temperature is None or self.humidity is None):
            try:
                self.temperature = self.sensor.temperature
                self.humidity = self.sensor.humidity
                if (self.temperature is None or self.humidity is None):
                    print("DHT22 read error")
            except Exception as e:
                print(e)
                print(type(e))
                print("DHT22 not connected")
                break

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity

if __name__ == "__main__":
    dhts = []
    dhts.append(DHT22(board.D4))
    dhts.append(DHT22(board.D17))
    for i in range(5):
        for dht in dhts:
            dht.update()
            print(dht.getTemperature())
            print(dht.getHumidity())
            print()
'''
get the temperature values from the two DHT22 sensors in °C
'''
# def getTemperatureValues(): 
#     temperatureReadings = []
#     try:
#         for i in range(len(dhts)):
#             newTemperatureReading = {}
#             newTemperatureReading["index"] = i
#             newTemperatureReading["value"] = dhts[i].temperature
#             temperatureReadings.append(newTemperatureReading)
#     except Exception as e:
#         print('DHT22 temperature read error or not running on RPi')
#         print(e)
#         temperatureReadings = []
#         for i in range(len(dhts)):
#             newTemperatureReading = {}
#             newTemperatureReading["index"] = i
#             newTemperatureReading["value"] = -100
#             temperatureReadings.append(newTemperatureReading)
#     return temperatureReadings

# '''
# get the humidity values from the two DHT22 sensors in %
# '''
# def getHumidityValues():
#     humidityReadings = []
#     try:
#         for i in range(len(dhts)):
#             newHumidityReading = {}
#             newHumidityReading["index"] = i
#             newHumidityReading["value"] = dhts[i].humidity
#             humidityReadings.append(newHumidityReading)
#     except Exception as e:
#         print('DHT22 humidity read error or not running on RPi')
#         print(e)
#         humidityReadings = []
#         for i in range(len(dhts)):
#             newHumidityReading = {}
#             newHumidityReading["index"] = i
#             newHumidityReading["value"] = -1
#             humidityReadings.append(newHumidityReading)
#     return humidityReadings


