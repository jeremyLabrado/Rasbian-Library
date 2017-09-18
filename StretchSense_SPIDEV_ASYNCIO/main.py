#!/usr/bin/env python3
from __future__ import print_function
import stretchSenseLibrary


stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()


def main():

    scanTime = 3

    stretchsenseObject.Scanning(scanTime)
    stretchsenseObject.printAllSensorsAvailable()
    stretchsenseObject.connectAllPeripheral()
    stretchsenseObject.waitNotifications()
    while(1):
        stretchsenseObject.listToCsv()
    stretchsenseObject.disconnectAllPeripheral()
    stretchsenseObject.printAllSensorsConnected()


if __name__ == "__main__":
    main()
