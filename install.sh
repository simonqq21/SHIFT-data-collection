#!/bin/bash
install_dir=/home/pi/SHIFT-data-collection
sudo apt-get update
sudo apt-get install python3-pip apt-offline libatlas3-base i2c-tools

if [ ! -f $install_dir ]; then 
    echo "copying files..."
    mkdir -p $install_dir
    sudo cp -r * $install_dir
fi 

sudo pip3 install -r requirements.txt
sudo cp blast_camera.service /lib/systemd/system
sudo cp blast_lights.service /lib/systemd/system
sudo cp blast_mainserver.service /lib/systemd/system
sudo cp blast_pumps.service /lib/systemd/system
sudo cp blast_sensors.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable blast_camera.service
sudo systemctl enable blast_lights.service
sudo systemctl enable blast_mainserver.service
sudo systemctl enable blast_pumps.service
sudo systemctl enable blast_sensors.service
echo -n 'Reboot? (y/n) '
read ans
echo $ans
if [ $ans == 'y' ]; then
  sudo reboot
fi
