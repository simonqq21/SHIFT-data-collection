from datetime import datetime, date, time 
import os 
# MQTT broker 
mqttIP = "ccscloud2.dlsu.edu.ph"
mqttPort = 20010
clientname = "DLSU_SHIFT"
# MQTT data constants
expt_num = 0 
sitename = "DLSU-BLAST"
# MQTT topics 
main_topic = "sensor/dlsu/node-1/"
suffix_temperature = "temperature"
suffix_humidity = "humidity"
suffix_lightintensity = "light_intensity"
suffix_soilmoisture = "soil_moisture"
suffix_pH = "solution_pH"
suffix_EC = "solution_EC"
suffix_camera = "camera"

# csv filepath and filename 
csv_filepath = "/home/pi/blast/csv/"
csv_filename = "BLAST_sensors.csv"
# image filepath and filename 
images_filepath = "/home/pi/blast/images/"
images_filename_format = "IMG_{}.jpg"
# create image filepath if it doesn't exist 
debug = 1

sensor_data = {
    'datetime': [],
    'expt_num': [],
    'sitename': [],
    'type': [],
    'index': [],
    'value': [],
}

image_data = {
    'expt_num': [],
    'sitename': [],
    'type': [],
    'index': [],
    'filename': [],
    'imagedata': [],
}

camera_columns = ["type", "index", "filename", "binary_image"]
sensor_logging_start = time(hour=0, minute=0)
sensor_logging_end = time(hour=23, minute=59)

program_root = os.path.realpath(os.path.dirname(__file__))