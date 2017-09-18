# StretchSense, Raspberry Pi Library

Developed by Louis Germain the 25/07/2017
Contact : support@stretchsense.com

StretchSense is a global supplier of soft sensors. These soft sensors are perfect for measuring the complex movements of people and soft objects in our environment.

## About
### Background
The StretchSense Raspberry Pi Software has been developed to enable communication between a BLE shielded StretchSense circuit and a BLE enabled Raspberry Pi 3 Model B board.
Or a wired connection between a StretchSense Circuit and the Raspberry Pi 3 Model B board via SPI0 port. This library was developed using Ninja-IDE 2.3 with Python 3.4.2. First download and unzip the StretchSense Library from https://github.com/StretchSense.

### Usage

The StretchSense API includes a Library .py file which can be included in a Python developed project to enable BLE or SPI communications with a StretchSense circuit. The API also includes two other .py file which one represents two basic functional examples of using BLE or SPI and the other one contains the Python code to use the GUI.

## Documentation

Documentation of the .py files is available  in .html format locally at ../StretchSense/docs/_build/html/

## Installation

Please follow the instructions of the 'TO INSTALL.txt' file to install the StretchSense Library correctly

## Adding the Library to your application

Once your Python file is created, you have to import the StretchSense Library. To do so, it is like any other Python libraries:
1. Open your .py file.
2. Write "from StretchSense import stretchSenseLibrary" at the top of your file.

Then to use the functions you need to create an object named as you want, for example :"stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()".
This object will allow you to call every function or variable in the StretchSense API.

## Startup - using the terminal

In the StrechSense folder you have downloaded, you can see three .py files, stretchSenseLibrary.py which reprensents the library, main.py which contains two short functional examples and StretchSenseMain.py which contains the code for the GUI.

* Always run your programs as sudo and using python3 as they were developed this way.

* Ensure your device is properly connected:

BLE : if you want to use the BLE communication, make sure that your BLE circuit is turned on.
SPI : if you want to use the SPI communication, make sure that your circuit is connected to the SPI0 port.

If devices are not turned on or connected :

- BLE : it will terminate the program after scanning for 3 seconds.
- SPI : it will stream ten 0.0 values continuously until the end of the timer.

The steps required to use the examples.

* BLE Command lines :
	* Go to the location of the StretchSense folder : cd yourpath/StretchSense/BLE\ Example/
	* Run the exampleBle.py file : sudo python3 exampleBle.py

* SPI Command lines :
	* Go to the location of the StretchSense folder : cd yourpath/StretchSense/SPI\ Example/
	* Run the exampleSpi.py file : sudo python3 exampleSpi.py

If at any moment you want to stop the streaming before the end of the timer, use Ctrl+C in the terminal window.

## Startup - using the software

During the installation we have copied the StretchSense icon on your desktop. By double-clicking on it, it will open the StretchSense Software. Once opened, you can choose to display values using SPI communication or using BLE by clicking on the different icons.

* SPI : Choosing to display SPI communication, you will see the streaming of your values instantally and you can choose your settings by changing them in the settings tab located in the upper-right corner.
* BLE : Choosing to display BLE communication, you will first need to scan for devices by clicking on the Bluetooth sign button on the upper-right corner and start scanning. Once it is done, go back to the first BLE page and click on "Value Table" and the stream of values for the connected device will start.

## Compatible Devices

### Bluetooth
This library has been developed exclusively for Bluetooth 4.0 (BLE), also known as Bluetooth Low Energy. Compatible devices and circuits are listed below.

### StretchSense
- The StretchSense fabric Evaluation circuit is compatible with the support library.
- The StretchSense 10 Channel SPI with Bluetooth Shield Adapter is compatible with the support library.

### Raspberry Pi (Raspbian GNU/Linux 8 "Jessie")

#### Bluetooth Low Energy
BLE has been tested and developed on a Raspberry Pi 3 Model B.

The following Raspberry boards can use Bluetooth 4.0 (without Bluetooth dongle):

* Raspberry Pi 3 Model B

#### Serial Peripheral Interface
SPI has been tested and developed on a Raspberry Pi 3 Model B. 
For SPI connections - We recommend the use of the custom 'StretchSense Adapter for Raspberry Pi' shield rather than the use of wired methods. Contact sales@stretchsense.com

The following Raspberry Pi boards can use SPI :

* Raspberry Pi 3 Model B
* Raspberry Pi 2 Model B
* Rapsberry Pi 1 Model B+, A+
* Raspberry Pi Zero, Zero W

## License
The StretchSense Bluetooth LE & SPI Raspberry Pi Communication Library's is available under the MIT License attached within the root directory of this project.