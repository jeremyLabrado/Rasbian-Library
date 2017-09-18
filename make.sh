#!/bin/bash
cd 
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python
sudo apt-get install python3
sudo apt-get install python-pip libglib2.0-dev
sudo pip install bluepy
sudo apt-get install python3-pip libglib2.0-dev
sudo pip3 install bluepy
sudo apt-get install python-dev
sudo apt-get install python3-dev
git clone git://github.com/doceme/py-spidev
cd py-spidev
sudo python setup.py install
sudo python3 setup.py install
cd ..
sudo rm -r py-spidev
sudo apt-get install python-pyqt4
sudo apt-get install python3-pyqt4
sudo apt-get install qt4-designer
cd /home/pi/Desktop/StretchSense/
sudo chmod 0777 StretchSenseMain.py
sudo chmod 0777 main.py
sudo chmod 0777 stretchSenseLibrary.py
sudo chmod 0777 ressources_rc.py
cd /home/pi/Desktop/StretchSense/BLE\ Example/
sudo chmod 0777 exampleBle.py
cd /home/pi/Desktop/StretchSense/SPI\ Example/
sudo chmod 0777 exampleSpi.py
cd 
sudo cp -r /home/pi/Desktop/StretchSense /usr/share/applications/
sudo cp -r /home/pi/Desktop/StretchSense /usr/local/lib/python2.7/dist-packages/
sudo cp -r /home/pi/Desktop/StretchSense /usr/local/lib/python3.4/dist-packages/
sudo cp /usr/share/applications/StretchSense/_Icons/StretchSense_Logo_Blue_resized_64x64.png /usr/share/pixmaps/
sudo cp /usr/share/applications/StretchSense/StretchSense.icon /home/pi/Desktop/
sudo rm -r /home/pi/Desktop/StretchSense