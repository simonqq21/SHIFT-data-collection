from time import sleep
# import os 
# print(os.getcwd())
try:
    import adafruit_dht
except Exception as e:
    print("DHT library not present or not running on RPi")
    print(e)
try:
    from hardware.pi_interfaces import onewires
except:
    pass

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
        for i in range(5):
            if (self.temperature):
                break
            try:
                self.temperature = self.sensor.temperature
            except RuntimeError as err:
                print(err)
            except OverflowError as err:
                print(err)
            sleep(2)
        if (self.temperature is None):
            self.temperature = self.prevTemperature
        else:
            self.prevTemperature = self.temperature
        return self.temperature

    def getHumidity(self):
        self.humidity = None
        for i in range(5):
            if (self.humidity is not None):
                break
            try:
                self.humidity = self.sensor.humidity
            except RuntimeError as err:
                print(err)
            except OverflowError as err:
                print(err)
            sleep(2)
        if (self.humidity is None):
            self.humidity = self.prevHumidity
        else:
            self.prevHumidity = self.humidity
        return self.humidity

# driver code
if __name__ == "__main__":
    from pi_interfaces import onewires
    dhts = []
    for wire in onewires:
        dhts.append(DHT22(wire))
    for i in range(5):
        for dht in dhts:
            print(dht.getTemperature())
            print(dht.getHumidity())
            print()
            
