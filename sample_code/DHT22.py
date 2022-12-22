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

# dht = adafruit_dht.DHT22(board.D4)
# temperature = 0
# humidity = 0
#
# while True:
#     try:
#         temperature = dht.temperature
#         humidity = dht.humidity
#
#     except Exception as e:
#         print('read error ')
#         print(e)
#
#     print("temp={}, humd={}".format(temperature, humidity))
#     time.sleep(3)

dhts = []
print(board)
dhts.append(adafruit_dht.DHT22(board.D4))
dhts.append(adafruit_dht.DHT22(board.D17))
temperatures = [0]*2
humidities = [0]*2

while True:
    try:
        for i in range(len(dhts)):
            temperatures[i] = dhts[i].temperature
            humidities[i] = dhts[i].humidity

    except Exception as e:
        print('read error ')
        print(e)

    for i in range(len(dhts)):
        print("temp[{}]={}, humd[{}]={}".format(i, temperatures[i], i, humidities[i]))

    time.sleep(3000)
