'''
read and print temperature and humidity values from two DHT22 sensors connected
to GPIO pins 4 and 17
'''
import time
import board
try:
    import adafruit_dht
except:
    print("DHT library not present")

dhts = []
dhts.append(adafruit_dht.DHT22(board.D4))
dhts.append(adafruit_dht.DHT22(board.D17))
temperatures = [0]*2
humidities = [0]*2

while True:
    for i in range(len(dhts)):
        temperatures[i] = dht.temperature
        humidities[i] = dht.humidity

    for i in range(len(dhts)):
        print("temp["+str(i)+"]="+str(temperature)+", humd["+str(i)+"]="+str(humidity))
    time.sleep(3000)
