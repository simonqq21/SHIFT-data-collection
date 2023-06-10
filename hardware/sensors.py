'''
read and print analog values from nine analog soil moisture sensors, pH sensor, and
EC sensor from three ADS1115 i2c ADC modules
convert analog soil moisture sensor values into %, convert pH sensor values into
pH, and EC sensor values into EC (μS/cm).
'''
import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

import paho.mqtt.client as mqtt
import pandas as pd

from time import sleep 
from datetime import date, datetime, time, timedelta
from config import Config 
from email_sender import emailCrashed

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

class Sensors():
    def __init__(self):
        # create directories for collected data 
        os.makedirs(Config.csv_filepath, exist_ok=True)
        # create csv file for sensor data if it doesnt exist 
        df = pd.DataFrame.from_dict(Config.sensor_data, orient='columns')
        mode = 'w'
        index=False
        header=True
        if os.path.exists(Config.csv_filepath + Config.csv_filename):
            mode = 'a'
            header=False
            print('exists!')
        df.to_csv(Config.csv_filepath + Config.csv_filename, mode=mode, index=index, header=header) 
        self.columns = df.columns.values
        print(self.columns)
        self.datetimenow = datetime.now()

        # mqtt client init
        try:
            self.client = mqtt.Client(Config.clientname)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_publish = self.on_publish
            self.client.connect(Config.mqttIP, Config.mqttPort)
            print(self.client)
            self.client.loop_start()
        except Exception as e:
            print("Failed to connect to broker!")
            emailCrashed("PGMS sensors broker", self.datetimenow, e)
            print(e)

        # initialize onewire DHT22 temperature and humidity sensors 
        self.dhts = []
        for wire in onewires:
            self.dhts.append(DHT22(wire))
        
        # initialize TCA9548A i2c multiplexer and i2c BH1750 light intensity sensors 
        self.bhcount = 9
        self.tca = TCA9548A(i2c)
        print(self.tca)
        for si in range(self.bhcount):
            try:
                self.tca.addBH1750(si)
            except Exception as e:
                print(e)
                print("not running on Pi or device not connected properly") 

        # initialize ADS1115 i2c ADCs and analog channels for soil moisture sensors, PH4502C pH sensor, and TDS meter EC sensor 
        self.adss = []
        self.adss.append(ADS1115(i2c, addressIndex=0)) # soil moisture sensors 0-3
        self.adss.append(ADS1115(i2c, addressIndex=1)) # soil moisture sensors 4-7
        self.adss.append(ADS1115(i2c, addressIndex=2)) # soil moisture sensor 8, pH sensor, and EC sensor
        # add 9 soil moisture sensors throughout three ADS1115 consecutively from channel 0 of ADS1115 index 0
        # previous calibration
        # self.adss[0].addSoilMoistureSensor(m=-1.98019802, b=7.762376238)
        # self.adss[0].addSoilMoistureSensor(m=-0.7518796992, b=2.917293233)
        # self.adss[0].addSoilMoistureSensor(m=-1.007049345, b=3.917421954)
        # self.adss[0].addSoilMoistureSensor(m=-1.879699248, b=7.612781955)
        # self.adss[1].addSoilMoistureSensor(m=-2.127659574, b=8.765957447)
        # self.adss[1].addSoilMoistureSensor(m=-2.192982456, b=9.035087719)
        # self.adss[1].addSoilMoistureSensor(m=-2.487562189, b=10.2238806)
        # self.adss[1].addSoilMoistureSensor(m=-2.049180328, b=8.422131148)
        # self.adss[2].addSoilMoistureSensor(m=-2.049180328, b=8.422131148)

        # current calibration
        self.adss[0].addSoilMoistureSensor(m=-1.61, b=6.16)
        self.adss[0].addSoilMoistureSensor(m=-1.03, b=4.05)
        self.adss[0].addSoilMoistureSensor(m=-1.09, b=4.28)
        self.adss[0].addSoilMoistureSensor(m=-1.97, b=8.17)
        self.adss[1].addSoilMoistureSensor(m=-2.97, b=6.74)
        self.adss[1].addSoilMoistureSensor(m=-2.46, b=10.2)
        self.adss[1].addSoilMoistureSensor(m=-2.26, b=9.39)
        self.adss[1].addSoilMoistureSensor(m=-1.84, b=7.76)
        self.adss[2].addSoilMoistureSensor(m=-2.06, b=4.74)

        # add 1 pH sensor to channel 1 of ADS1115 index 2
        self.adss[2].addPH4502C(m=-0.1723776224, b=3.77251049)
        # add 1 EC sensor 
        self.adss[2].addTDSMeter()

    '''
    callback functions for MQTT broker
    '''
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        print(msg.topic)

    def on_publish(self, client, username, mid):
        print("Message published")

    '''
    return a dataframe containing the indexed sensor data to be transmitted
    '''
    def processSensorDataForPublishing(self, datetime, type, index, rawsensordata):
        data = Config.sensor_data
        data["datetime"] = [datetime]
        data["expt_num"] = [Config.expt_num]
        data["sitename"]= [Config.sitename]
        data["type"]= [type]
        data["index"]= [index]
        data["value"]= [rawsensordata]
        df = pd.DataFrame(data, columns=self.columns)
        if Config.debug:
            print(df)
        return df 

    '''
    save the sensor data dataframe to the local CSV file and transmit the sensor data 
    dataframe to the MQTT main_topic
    '''
    def saveAndPublishData(self, df, sensorPublishTopic):
        if Config.debug:
            print(df)
        df.to_csv(Config.csv_filepath + Config.csv_filename, mode='a', index=False, header=False)
        try:
            self.client.publish(sensorPublishTopic, df.to_json())
        except Exception as e:
            print("Publish failed, check broker")
            emailCrashed("PGMS sensors broker", self.datetimenow, e)


    def captureTemperatures(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # temperature from DHT22 
        index = 0
        for dht in self.dhts:
            curr_temperature = dht.getTemperature()
            df_temperature = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_temperature, index, curr_temperature)
            self.saveAndPublishData(df_temperature, Config.main_topic+Config.suffix_temperature)
            index += 1

    def captureHumidities(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # humidity from DHT22 
        index = 0
        for dht in self.dhts:
            curr_humidity = dht.getHumidity()
            df_humidity = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_humidity, index, curr_humidity)
            self.saveAndPublishData(df_humidity, Config.main_topic+Config.suffix_humidity)
            index += 1

    def captureLightIntensities(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # light intensity from BH1750 
        curr_lightIntensities = self.tca.getLightIntensities()
        index = 0
        for li in curr_lightIntensities:
            df_lightintensity = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_lightintensity, index, li)
            self.saveAndPublishData(df_lightintensity, Config.main_topic+Config.suffix_lightintensity)
            index += 1
        print(f"light index={index}")

    def captureSoilMoistures(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # soil moisture from soil moisture sensors
        curr_soilmoistures = [] 
        for ads in self.adss:
            for sm in ads.getSoilMoistures():
                curr_soilmoistures.append(sm)
        index = 0 
        for sm in curr_soilmoistures:
            df_soilmoisture = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_soilmoisture, index, sm)
            self.saveAndPublishData(df_soilmoisture, Config.main_topic+Config.suffix_soilmoisture)
            index += 1 

    def capturePHs(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # pH from PH-4502C 
        curr_solutionpHs = [] 
        for ads in self.adss:
            for pH in ads.getSolutionpHs():
                curr_solutionpHs.append(pH)
        index = 0 
        for pH in curr_solutionpHs:
            df_solutionpH = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_pH, index, pH)
            self.saveAndPublishData(df_solutionpH, Config.main_topic+Config.suffix_pH)
            index += 1 

    def captureECs(self):
        sensorTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        # EC from TDS Meter 1.0 
        curr_solutionECs = [] 
        for ads in self.adss:
            for ec in ads.getSolutionECs():
                curr_solutionECs.append(ec)
        index = 0 
        for ec in curr_solutionECs:
            df_solutionEC = self.processSensorDataForPublishing(sensorTimeStamp, Config.suffix_EC, index, ec)
            self.saveAndPublishData(df_solutionEC, Config.main_topic+Config.suffix_EC)
            index += 1 

    '''
    method to capture all kinds of sensors into the CSV file and transmit it via MQTT
    '''
    def captureSensors(self):
        self.captureTemperatures()
        self.captureHumidities()
        self.captureLightIntensities()
        self.captureSoilMoistures()
        self.capturePHs()
        self.captureECs()
        
        
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
        valid_readings = 0
        total_temp = 0
        for i in range(5):
            try:
                total_temp += self.sensor.temperature
                valid_readings += 1 
            except RuntimeError as err:
                print("runtime error") 
                print(err)
            except OverflowError as err:
                print("overflow error")
                print(err)
            sleep(2)
        if (valid_readings > 0):
            self.temperature = total_temp / valid_readings
            self.prevTemperature = self.temperature
        else:
            self.temperature = self.prevTemperature
        return self.temperature

    def getHumidity(self):
        self.humidity = None
        valid_readings = 0
        total_humd = 0
        for i in range(5):
            try:
                total_humd += self.sensor.humidity
                valid_readings += 1
            except RuntimeError as err:
                print("runtime error") 
                print(err)
            except OverflowError as err:
                print("overflow error")
                print(err)
            sleep(2)
        if (valid_readings > 0):
            self.humidity = total_humd / valid_readings
            self.prevHumidity = self.humidity
        else:
            self.humidity = self.prevHumidity
        return self.humidity

class SoilMoistureSensor:
    def __init__(self, ADSchan, m, b):
        self.type = "soil_moisture"
        self.chan = ADSchan
        self.voltage = None
        self.soilMoisture = None 
        # calibration data 
        self.m = m
        self.b = b

    def getSoilMoisture(self):
        try:
            self.voltage = self.chan.voltage
            self.soilMoisture = self.voltage * self.m + self.b    
            if self.soilMoisture < 0:
                self.soilMoisture = 0 
            elif self.soilMoisture > 1:
                self.soilMoisture = 1
            if Config.debug:
                print(f"sm_voltage = {self.voltage}")
        except:
            print("ADS1115 not connected properly")
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

    def getSolutionpH(self):
        try:
            self.voltage = self.chan.voltage
            self.pH = self.voltage * self.m + self.b  
            if Config.debug: 
                print(f"ph_voltage = {self.voltage}")
        except:
            print("ADS1115 not connected properly")
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

    def getSolutionEC(self, water_temperature):
        self.compensationCoefficient = 1.0 + 0.02 *(water_temperature-25.0)
        try:
            self.voltage = self.chan.voltage
            self.compensationVoltage = self.voltage / self.compensationCoefficient
            self.TDS = (133.42*self.compensationVoltage**3 - 255.86*self.compensationVoltage**2 + 857.39*self.compensationVoltage)*0.5
            self.EC = self.TDS / 500  
            if Config.debug:
                print(f"ec_voltage = {self.voltage}")
        except:
            print("ADS1115 not connected properly")
        return self.EC

class ADS1115:
    def __init__(self, i2c, gain=1, addressIndex=0): # gain=1 to fit the 3v3 range 
        self.gain = gain
        self.address = 72 + addressIndex
        self.chans = []  
        self.sensors = []   
        try:   
            self.ads = ADS.ADS1115(i2c, gain=self.gain, address=self.address)  
            self.chans.append(AnalogIn(self.ads, ADS.P0))
            self.chans.append(AnalogIn(self.ads, ADS.P1))
            self.chans.append(AnalogIn(self.ads, ADS.P2))
            self.chans.append(AnalogIn(self.ads, ADS.P3))
        except Exception as err:
            print(f"Error: {err}")

    def addSoilMoistureSensor(self, m, b):
        if (len(self.sensors) >= 4):
            print("ADS1115 is full, error adding soil moisture sensor")
        else:
            chanIndex = len(self.sensors) - 1 if len(self.sensors) > 0 else 0
            if Config.debug:
                print(chanIndex)
                print(self.chans)
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
        if Config.debug:
            print("sm")
        soilmoisture_values = []
        for sensor in self.sensors:
            if sensor.type == "soil_moisture":
                if Config.debug:
                    print(sensor.voltage)
                soilmoisture_values.append(sensor.getSoilMoisture())
        if Config.debug:
            print()
        return soilmoisture_values

    def getSolutionpHs(self):
        if Config.debug:
            print("ph")
        solutionpH_values = []
        for sensor in self.sensors:
            if sensor.type == "solution_pH":
                if Config.debug:
                    print(sensor.voltage)
                solutionpH_values.append(sensor.getSolutionpH())
        if Config.debug:
            print()
        return solutionpH_values 

    def getSolutionECs(self, water_temperature=25):
        if Config.debug:
            print("ec")
        solutionEC_values = []
        for sensor in self.sensors:
            if sensor.type == "solution_EC":
                if Config.debug:
                    print(sensor.voltage)
                solutionEC_values.append(sensor.getSolutionEC(water_temperature))
        if Config.debug:
            print()
        return solutionEC_values  

class BH1750:
    def __init__(self, i2c, altAddr=False):
        try:
            if altAddr:
                self.sensor = adafruit_bh1750.BH1750(i2c, address=92)
            else:
                self.sensor = adafruit_bh1750.BH1750(i2c)
        except:
            print("error adding BH1750 on channel {}".format(i2c))
        self.lightintensity = None

    def getLightIntensity(self):
        sleep(0.5)
        self.lightintensity = None
        for i in range(5):  
            try:
                self.lightintensity = self.sensor.lux
                break
            except Exception as err:
                print(err)
            sleep(0.5) 
        return self.lightintensity

class TCA9548A:
    def __init__(self, i2c, address=112):
        self.bhs = []
        try:
            self.tca = adafruit_tca9548a.TCA9548A(i2c, address=address) 
        except:
            print("error adding TCA9548 on channel {}".format(i2c))
        
    def addBH1750(self, i2cIndex):
        try:
            if (i2cIndex > 7):
                self.bhs.append(BH1750(self.tca[i2cIndex%8], altAddr=True))
            else:
                self.bhs.append(BH1750(self.tca[i2cIndex%8]))
        except Exception as err:
            print(err)
        
    def getLightIntensities(self):
        self.lightIntensities = []
        print(len(self.bhs))
        for bh in self.bhs:
            self.lightIntensities.append(bh.getLightIntensity())
        return self.lightIntensities
