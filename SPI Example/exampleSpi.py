#!/usr/bin/env python3
from __future__ import print_function
from StretchSense import stretchSenseLibrary

"""

    - Website : https://www.stretchsense.com

    - Important : This StretchSense Library has been designed to enable the connection of one or more "StretchSense Sensor" and "StretchSense IC Boards" to your Raspberry Pi

    - Author : Louis Germain

    - Copyright : 2017 StretchSense

    - Date : 26/07/2017

    - Version : 1.0.0

"""

stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()

BLE_MODE = 0x00
SPI_MODE = 0x01


def mainBle():
    #print("mainBle()")

    """
    BLE main example.

    Those following lines are used to connect every StretchSense devices around and then stream
    their values into a terminal in a .csv format.

    Make sure that timeBreak is superior to 0, and the program will run for the processor time you gave him.

    Make sure that the correct BLE_MODE is selected at the end of the file.

    To run the mainBle() function open a terminal, go to the folder where main.py file is
    located.

    And enter the following command line :

        $ sudo python3 main.py

    """

    def updateValue():
        #print("updateValues()")

        timePassed = stretchSenseLibrary.time.clock()
        timeBreak = 5                                        # Choose the processor time to finish the program

        if timePassed < timeBreak:
            stretchsenseObject.waitNotifications()
            stretchsenseObject.listToCsv()
            stretchSenseLibrary.time.sleep(0.1)
        else:
            t.stop()
            pass

    timeToScan = 3
    stretchsenseObject.scanning(timeToScan)
    stretchsenseObject.printAllSensorsAvailable()
    stretchsenseObject.connectAllPeripheral()
    stretchsenseObject.waitNotifications()
    stretchsenseObject.listToCsv()
    numberOfPeripheralConnected = len(stretchsenseObject.getListPeripheralIsConnected())

    if numberOfPeripheralConnected > 0:

        t = stretchSenseLibrary.RepeatedTimer(0.01, lambda: updateValue())
    else:
        pass


def mainSpi():
    #print("mainSpi()")

    """
    SPI main example.

    Those following lines are used to stream the values of a 16FGV1.0 device from StretchSense,
    connected to the SPI0 port of a Raspberry Pi .

    Make sure that timeBreak is superior than 0, and the program will run for the processor time you gave him.

    Make sure that the correct SPI_MODE is selected at the end of the file.

    To run the mainSpi() function open a terminal, go to the folder where main.py file is
    located.

    And enter the following command line :

        $ sudo python3 main.py

    """
    def updateValueSpi():
        #print("updateValueSpi()")

        timePassed = stretchSenseLibrary.time.clock()
        timeBreak = 5                                        # Choose the processor time to finish the program

        if timePassed < timeBreak:
            stretchsenseObject.continuousModeCapacitance()
            stretchsenseObject.listToCsvSpi()
            stretchSenseLibrary.time.sleep(0.1)
        else:
            stretchsenseObject.closeSpi()
            t.stop()
            pass

    stretchsenseObject.spiSetup()
    numberOfSpiPeripheralConnected = len(stretchsenseObject.getListPeripheralSpi())

    if numberOfSpiPeripheralConnected > 0:

        t = stretchSenseLibrary.RepeatedTimer(0.01, lambda: updateValueSpi())

    else:
        pass


if __name__ == "__main__":

    mode = SPI_MODE

    if mode == SPI_MODE:
        mainSpi()
    elif mode == BLE_MODE:
        mainBle()
    else:
        pass
