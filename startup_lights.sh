#!/bin/bash
app_path=$(dirname $(realpath "$0"))
echo $app_path
sudo python3 $app_path/lights_client.py
exit