import time
import adafruit_dht
import board

dht = adafruit_dht.DHT22(board.D17)
while True:
    temperature = dht.temperature
    humidity = dht.humidity
    print("temp="+str(temperature)+", humd="+str(humidity))
    time.sleep(3000)
