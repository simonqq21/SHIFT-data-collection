'''
read and print analog values from nine analog soil moisture sensors, pH sensor, and
EC sensor from three ADS1115 i2c ADC modules
convert analog soil moisture sensor values into %, convert pH sensor values into
pH, and EC sensor values into EC (μS/cm).

'''

from time import sleep 
try:
    from hardware.pi_interfaces import i2c 
    from hardware.pi_interfaces import onewires
except:
    pass
try:
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("ads1115 library not present")
try:
    import adafruit_dht
except:
    print("DHT library not present or not running on RPi")
try:
    import adafruit_tca9548a
    import adafruit_bh1750
except:
    print("BH1750 or TCA9548A library not present")