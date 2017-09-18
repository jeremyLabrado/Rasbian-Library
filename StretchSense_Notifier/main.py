#!/usr/bin/env python3
from __future__ import print_function
import stretchSenseLibrary


stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()
defaultCenter = stretchSenseLibrary.NotificationCenter()


def main():

    scanTime = 5

    stretchsenseObject.Scanning(scanTime)
    stretchsenseObject.connectAllPeripheral()
    numberOfPeripheralConnected = len(stretchsenseObject.getListPeripheralIsConnected())

    #while(numberOfPeripheralConnected > 0):
    defaultCenter.addObserver(stretchsenseObject.waitNotifications(), "UpdateValueNotification", None)

    stretchsenseObject.disconnectAllPeripheral()
    stretchsenseObject.printAllSensorsConnected()

if __name__ == "__main__":
    main()