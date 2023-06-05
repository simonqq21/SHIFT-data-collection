#!/bin/bash 
sudo kill $(ps -e -o pid,cmd | grep lights_client | grep python3 | cut -d' ' -f3)
sudo kill $(ps -e -o pid,cmd | grep pumps_client | grep python3 | cut -d' ' -f3)
sudo kill $(ps -e -o pid,cmd | grep camera_client | grep python3 | cut -d' ' -f3)
sudo kill $(ps -e -o pid,cmd | grep sensors_client | grep python3 | cut -d' ' -f3)
sudo kill $(ps -e -o pid,cmd | grep mainserver | grep python3 | cut -d' ' -f3)