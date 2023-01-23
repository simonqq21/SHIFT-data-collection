# This program automates sending of dummy data to the MQTT broker

import paho.mqtt.client as mqtt
import time
import json
import binascii
from datetime import datetime
import paho.mqtt.publish as publish
import random


def get_rand_value(data_type):
    if data_type == "light_intensity":
        value = random.uniform(0,500)
    elif data_type == "temperature":
        value = random.uniform(25.1,28.7)
    elif data_type == "humidity":
        value = random.uniform(71,85)  
    elif data_type == "soil_moisture":
        value = random.uniform(10,45)  
    elif data_type == "solution_pH":
        value = random.uniform(0,14)  
    elif data_type == "solution_EC":
        value = random.uniform(179.3,192.14) 
    elif data_type == "solution_TDS":
        value = random.uniform(50,150)   

    return value

def get_data():
    data_types = ["temperature", "humidity", "light_intensity", "soil_moisture", "solution_pH", "solution_EC", "solution_TDS"]
    data_type = random.choice(data_types)
    value = get_rand_value(data_type)

    brokers_out = {
        'datetime': {'0': datetime.now().strftime('%m/%d/%Y %H:%M')},
        'expt_num': {'0': '1'},
        'sitename': {'0': 'dlsu_blast'},
        'type': {'0': data_type},
        'index': {'0':random.randint(0,8)},
        'value': {'0': value}
    }
    data_out = json.dumps(brokers_out)
    return data_out, data_type

def on_publish(client, usedata, mid):
    print("Message published...")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("sensor/dlsu/node-1/temperature")
    data_out, data_type = get_data()
    # topic = "sensor/dlsu/node-1/" + data_type
    # print(topic)
    for i in range(1000):
        data_out, data_type = get_data()
        topic = "sensor/dlsu/node-1/" + data_type
        print(topic)
        client.publish(
            topic, data_out)
        

def on_message(client, userdata, msg):
    print("In on message: ")
    print(" Line 28\n", msg.topic)
    print("Line 29\n", msg.payload)
    payload = json.loads(msg.payload)

    client.disconnect()



client = mqtt.Client(client_id="william", clean_session=False)

client.on_publish = on_publish
client.on_connect = on_connect
client.on_message = on_message


client.connect("ccscloud2.dlsu.edu.ph", 20010)
client.loop_forever()