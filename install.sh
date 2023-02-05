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
sudo cp blast_logger.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable blast_logger.service
echo -n 'Reboot? (y/n) '
read ans
echo $ans
if [ $ans == 'y' ]; then
  sudo reboot
fi
