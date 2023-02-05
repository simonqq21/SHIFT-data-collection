#!/bin/bash
app_path=$(dirname $(realpath "$0"))
sudo python3 $app_path/main.py
exit