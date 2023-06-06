import os 
import sys 
here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

from time import sleep
import json
from datetime import datetime, date, time, timedelta
import threading
from io import BytesIO

import numpy as np
import paho.mqtt.client as mqtt
import pandas as pd

try:
    from picamera import PiCamera
except Exception as e:
    print("picamera library not present")
    print("Exception = ")
    print(e)
import binascii
from config import Config 
from email_sender import emailCrashed

class Camera():
    def __init__(self, images_filepath=Config.images_filepath, images_filename_format=Config.images_filename_format): 
        self.imageStream = BytesIO()
        self.binaryImage = None
        # flag to indicate if an image is currently being captured
        self.lastTimePhotoTaken = datetime(year=1970, month=1, day=1)
        self.images_filepath = images_filepath
        self.images_filename_format = images_filename_format
        self.filename = "" 
        self.datetimenow = datetime.now()

        # create directories for collected data 
        os.makedirs(Config.images_filepath, exist_ok=True)
        # columns for image dataframe
        self.camera_columns = np.array(list(Config.image_data.keys()))
        print(self.camera_columns) 

        # initialize the MQTT client 
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
            emailCrashed("PGMS camera broker", self.datetimenow, e)
            print(e)  

        # initialize camera object
        try:
            self.camera = PiCamera()
            try:
                self.camera.resolution = (3280, 2464)
            except Exception as err:
                self.camera.resolution = (2592, 1944)
        except:
            print("Failed to create camera object!")

#         self.loadGrowLightIntervals(growLightsIntervalsFilename)
#         self.loadCameraIntervals(cameraIntervalsFilename)
#         self.getGrowLightIntervalsPerDay()
#         self.getCameraIntervalsPerDay()

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
    return a dataframe containing the image data and metadata to be transmitted
    '''
    def processImageDataForPublishing(self, type, index, filename, binaryImage):
        data = Config.image_data
        data["expt_num"] = [Config.expt_num]
        data["sitename"]= [Config.sitename]
        data["type"]= [type]
        data["index"]= [index]
        data["filename"]= [filename]
        data["imagedata"]= [binaryImage]
        df = pd.DataFrame(data, columns=self.camera_columns)
        if Config.debug:
            print(df)
        return df  

    '''
    publish the captured image dataframe to the MQTT broker
    '''
    def publishImage(self, df, imagePublishTopic):
        try:
            self.client.publish(imagePublishTopic, df.to_json())
        except:
            print("Publish failed, check broker")  
            
    # thread function to toggle the grow lights and camera lights and capture an image using the Pi Camera
    def captureImage(self, filepath=None, filename=None):
        self.imageStream = BytesIO()
        self.binaryImage = None
        
        if filepath is None:
            filepath=self.images_filepath 
        if filename is None:
            self.filename=self.images_filename_format.format(datetime.now().strftime("%Y%m%d_%H%M"))
        else:
            self.filename = filename
        try:
            self.camera.start_preview() 
            sleep(2)
            self.camera.capture(self.imageStream, 'jpeg')
            with open(filepath + self.filename, "wb") as f:
                f.write(self.imageStream.getbuffer())
            f.close()
            self.binaryImage = binascii.b2a_base64(self.imageStream.getvalue()).decode()
        except:
            print("no camera object, using dummy camera")
        print("image captured")
        sleep(0.5)
       
        try:
            self.camera.stop_preview()
        except:
            pass

        # transmit photo via MQTT 
        index=0
        cameraTimeStamp = datetime.now().strftime("%m/%d/%Y %H:%M")
        df_image = self.processImageDataForPublishing(Config.suffix_camera, index, self.filename, self.binaryImage)
        self.publishImage(df_image, Config.main_topic+Config.suffix_camera)
        if Config.debug:
            print("successfully transmitted image")
        return self.binaryImage




    



#     #wrapper function to capture an image every time the capture button is pressed 
#     def captureImageButton(self):
#         # change the filepath and filename
#         thread = threading.Thread(target=self.captureImage, daemon=True)
#         thread.start()

#     def pollGrowLights(self, datetimenow):
#         # loop to check switch grow lights
#         for dayinterval in self.growLightDailyIntervals:
#             # If the time is between the on and off time and the grow lights are off, switch them on.
#             print("{},{},{},{},".format(datetimenow >= dayinterval["on_time"], \
#                 datetimenow < dayinterval["off_time"], \
#                 self.growlightval, \
#                 self.pictureTaking))
#             print()
#             if (datetimenow >= dayinterval["on_time"] \
#                 and datetimenow < dayinterval["off_time"] \
#                 and not self.growlightval \
#                 and not self.pictureTaking):
#                 actualOnInterval = dayinterval["duration"] - (datetimenow - dayinterval["on_time"])
#                 thread = threading.Thread(target=self.growLightOn, args=(actualOnInterval, ), daemon=True)
#                 thread.start()

#     def pollCamera(self, datetimenow):
#         # loop to capture image 
#         for dayinterval in self.cameraDailyIntervals: 
#             if (datetimenow >= dayinterval["start_time"] \
#                 and datetimenow <= dayinterval["end_time"] \
#                 and datetime.now() - self.lastTimePhotoTaken >= dayinterval["interval"]):
#                 self.lastTimePhotoTaken = datetime.now()
#                 # change the filepath and filename
#                 thread = threading.Thread(target=self.captureImage, daemon=True)
#                 thread.start()

