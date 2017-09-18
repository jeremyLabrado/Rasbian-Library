#!/usr/bin/env python3

from __future__ import print_function
import argparse
import binascii
import os
import sys
from bluepy import btle


"""StretchSense Classes & generators for the different types of sensors

/////////////////////////////////////////////////////////////////////////

This is what you can change if there is update in the sensors declaration
or new types of sensors or anything else that you want to improve.

/////////////////////////////////////////////////////////////////////////

"""


class NotificationCenter(object):
    #print("\033[0;35;40m NotificationCenter()\033[0m")

    def __init__(self):
        #print("\033[0;35;40m NotificationCenter()__init__()\033[0m")

        self.notifications = {}
        self.observerKeys = {}

    def addObserver(self, observer, method, notificationName, observedObject=None):
        #print("\033[0;32;40m addObserver()\033[0m")

        if notificationName not in self.notifications:

            self.notifications[notificationName] = {}
        notificationDict = self.notifications[notificationName]

        if observedObject not in notificationDict:

            notificationDict[observedObject] = {}
        notificationDict[observedObject][observer] = method

        if observer not in self.observerKeys:

            self.observerKeys[observer] = []
        self.observerKeys[observer].append((notificationName, observedObject))

    def removeObserver(self, observer, notificationName=None, observedObject=None):
        print("\033[0;35;40m removeObserver()\033[0m")

        try:
            observerKeys = self.observerKeys.pop(observer)

        except KeyError:
            return

        for observerKey in observerKeys:

            if notificationName and observerKey[0] != notificationName:
                continue

            if observedObject and observerKey[1] != observedObject:
                continue

            try:
                self.notifications[observerKey[0]][observerKey[1]].pop(observer)
            except KeyError:
                return

            if len(self.notifications[observerKey[0]][observerKey[1]]) == 0:

                self.notifications[observerKey[0]].pop(observerKey[1])
                if len(self.notifications[observerKey[0]]) == 0:

                    self.notifications.pop(observerKey[0])

    def postNotification(self, notificationName, notifyingObject, userInfo=None):
        #print("\033[0;35;40m postNotification()\033[0m")

        try:
            notificationDict = self.notifications[notificationName]

        except KeyError:
            return

        for key in (notifyingObject, None):

            try:
                methodsDict = notificationDict[key]

            except KeyError:
                continue

            for observer in methodsDict:

                if not userInfo:
                    methodsDict[observer](notifyingObject)

                else:
                    methodsDict[observer](notifyingObject, userInfo)


class StretchSensePeripheral:
    #print("\033[0;35;40m StretchSensePeripheral()\033[0m")

    def __init__(self):
        #print("\033[0;35;40m __init__().StretchSensePeripheral()\033[0m")

        # Mac Address
        self.addr = ''

        # Unique Number Identifier
        self.uuid = ''

        # Current Capacitance value of the sensor
        self.value = 0x0000

        # A unique number for each sensor, based on the order when the sensor is connected to the device
        self.channelNumber = 0

        # Bool use to validate the display of the sensor in the graph
        self.display = True

        # Generation of the circuit, we initialize it at a Generation 2 which the common One-Channel sensor
        self.gen = 2


class StretchSenseAPI():
    #print("\033[0;35;40m StretchSenseAPI()\033[0m")

    """

    ////////////////////////////////////////

    Variables : Manager & Lists Peripherals

    ////////////////////////////////////////

    """
    # This is the list of the Peripheral we are using to connect

    listPeripheralInUse = [btle.Peripheral()]

    # This is the list of StretchSense Bluetooth peripherals detected by our device during a scan event

    listPeripheralAvailable = [StretchSensePeripheral()]

    # This is the list of StretchSense Bluetooth peripherals which are connected to our device after being scanned

    listPeripheralIsConnected = [StretchSensePeripheral()]

    # This is the list of StretchSense Bluetooth peripherals which are saved to our device after being connected once

    listPeripheralIsOnceConnected = [btle.Peripheral()]

    """

    ////////////////////////////////////////////

    Variables : Services & Characteristics UUID

    ///////////////////////////////////////////


    """

    # The name we use to filter Bluetooth scan results and find only StretchSense sensors
    deviceName = 'StretchSense'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense sensors Gen 3
    serviceUUID3 = '00001701-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense sensors Gen 3
    dataUUID3 = '00001702-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "shutdown characteristic" from StretchSense sensors Gen 3
    shutdownUUID3 = '00001704-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "samplingTime characteristic" from StretchSense sensors Gen 3
    samplingTimeUUID3 = '00001705-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "average characterisitc" from StretchSense sensors Gen 3
    averageUUID3 = '00001706-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense sensors Gen 2
    serviceUUID2 = '00001501-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense sensors Gen 2
    dataUUID2 = '00001502-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "shutdown characteristic" from StretchSense sensors Gen 2
    shutdownUUID2 = '00001504-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "samplingTime characteristic" from StretchSense sensors Gen 2
    samplingTimeUUID2 = '00001505-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "average characterisitc" from StretchSense sensors Gen 2
    averageUUID2 = '00001506-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense sensors Mimic
    serviceUUIDMimic = '00002001-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense sensors Mimic
    dataUUIDMimic = '00002002-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "shutdown characteristic" from StretchSense sensors Mimic
    shutdownUUIDMimic = '00002004-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "samplingTime characteristic" from StretchSense sensors Mimic
    samplingTimeUUIDMimic = '00002005-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "average characterisitc" from StretchSense sensors Mimic
    averageUUIDMimic = '00002006-7374-7265-7563-6873656e7365'

    """

    ////////////////////////////////

    Variables : Set sensors & info

    ////////////////////////////////


    """
    # Number of data samples within the filtering array

    numberOfSample = 30

    # Initialisation value of the sampling time value (SamplingTime = (value +1)*40ms)

    samplingTimeNumber = 0

    # Sized of the filter based on the number of samples

    filteringNumber = 0

    # Feedback from the sensor

    informationFeedBack = ''

    """

    ///////////////////////////

    Bluepy buffer Scanning class

    ///////////////////////////

    """

    class ScanPrint(btle.DefaultDelegate):
        #print("\033[0;33;40m ScanPrint()\033[0m")

        def __init__(self, opts):
            #print("\033[0;33;40m __init__().ScanPrint()\033[0m")
            btle.DefaultDelegate.__init__(self)
            self.opts = opts

        def handleDiscovery(self, dev, isNewDev, isNewData):
            #print("\033[0;33;40m handleDiscovery()\033[0m")

            if isNewDev:
                status = "new"
            elif isNewData:
                if self.opts.new:
                    return
                status = "update"
            else:
                if not self.opts.all:
                    return
                status = "old"

            if dev.rssi < self.opts.sensitivity:
                return

            if not dev.scanData:
                print ('\t(no data)')
            print()

    """

    /////////////////////////////////////////////////////

    Functions : Scan, Print, Connect/Disconnect & Update

    /////////////////////////////////////////////////////

    """

    def printAllSensorsAvailable(self):
        print("\033[0;35;40m printAllSensorsAvailable()\033[0m")

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1

        if (numberOfPeripheralAvailable == 0):
            return print("No sensors available")

        elif numberOfPeripheralAvailable >= 1:

            for myPeripheralAvailable in self.listPeripheralAvailable:

                if myPeripheralAvailable.addr != '':
                    print("StretchSense Sensor : %s\n" % (myPeripheralAvailable.addr))

    def printAllSensorsConnected(self):
        print("\033[0;35;40m printAllSensorsConnected()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected) - 1

        if (numberOfPeripheralConnected == 0):
            return print("No sensors connected")

        elif numberOfPeripheralConnected >= 1:

            for myPeripheralConnected in self.listPeripheralIsConnected:

                if myPeripheralConnected.addr != '':
                    print("StretchSense Sensor Connected : %s\n" % (myPeripheralConnected.addr))

    def Scanning(self, scanTime):
        print("\033[0;35;40m Scanning()\033[0m")

        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                            help='Interface number for scan')
        parser.add_argument('-t', '--timeout', action='store', type=int, default=4,
                            help='Scan delay, 0 for continuous')
        parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                            help='dBm value for filtering far devices')
        parser.add_argument('-d', '--discover', action='store_true',
                            help='Connect and discover service to scanned devices')
        parser.add_argument('-a', '--all', action='store_true',
                            help='Display duplicate adv responses, by default show new + updated')
        parser.add_argument('-n', '--new', action='store_true',
                            help='Display only new adv responses, by default show new + updated')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Increase output verbosity')
        arg = parser.parse_args(sys.argv[1:])

        self.Debugging = arg.verbose
        scanner = btle.Scanner(arg.hci).withDelegate(self.ScanPrint(arg))
        devicesAvailable = scanner.scan(scanTime)

        for devices in devicesAvailable:
            deviceAlreadyInTheList = False

            for (sdid, desc, val) in devices.getScanData():

                if (val == StretchSenseAPI.deviceName):

                    for myDeviceInTheList in self.listPeripheralAvailable:

                        if (myDeviceInTheList.addr == devices.addr):
                            deviceAlreadyInTheList = True

                    if deviceAlreadyInTheList is False:
                        self.listPeripheralAvailable.append(devices)

    def connectOnePeripheralWithAddress(self, deviceAddr):
        print("\033[0;35;40m connectOnePeripheralWithAddr()\033[0m")

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1

        if numberOfPeripheralAvailable != 0:

            for myPeripheralAvailable in self.listPeripheralAvailable:

                if myPeripheralAvailable.addr == deviceAddr:
                    print('Address we are trying to connect to : ', deviceAddr)
                    myPeripheralConnected = btle.Peripheral(myPeripheralAvailable)
                    myPeripheralConnected.setDelegate(StretchSenseDelegate())
                    self.listPeripheralIsConnected.append(myPeripheralConnected)

    def connectOnePeripheral(self, click):
        print("\033[0;35;40m connectOnePeripheral()\033[0m")

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1
        listDeviceToConnect = self.ListPeripheralAvailable()

        for device in listDeviceToConnect:

            if device.addr == click:

                if numberOfPeripheralAvailable != 0:

                    for myPeripheralAvailable in self.listPeripheralAvailable:

                        if myPeripheralAvailable.deviceAddr == device.addr:
                            print("Address we are trying to connect to : ", device.addr)
                            myPeripheralConnected = btle.Peripheral(myPeripheralAvailable)
                            myPeripheralConnected.setDelegate(StretchSenseDelegate())
                            self.listPeripheralIsConnected.append(myPeripheralConnected)

    def connectAllPeripheral(self):
        print("\033[0;35;40m connectAllPeripheral()\033[0m")

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1
        self.listPeripheralIsConnected = []
        self.listPeripheralInUse = []

        print("Number of StretchSense BLE scanned = ", numberOfPeripheralAvailable)

        if numberOfPeripheralAvailable > 0:

            for myPeripheralAvailable in self.listPeripheralAvailable:

                if myPeripheralAvailable.addr != '':
                    print('Address we are trying to connect to : ', myPeripheralAvailable.addr)
                    myPeripheralConnected = btle.Peripheral(myPeripheralAvailable)
                    myPeripheralConnected.setDelegate(StretchSenseDelegate(myPeripheralConnected))
                    myPeripheralConnected.deviceAddr = myPeripheralAvailable.addr
                    self.listPeripheralInUse.append(myPeripheralConnected)
                    listOfServices = sorted(myPeripheralConnected.services, key=lambda services: services.hndStart)

                    for services in listOfServices:

                        if services.hndStart == services.hndEnd:
                            continue

                        if services.uuid == self.serviceUUID2:
                            self.generateGen2(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, "\x01\x00")
                            continue

                        if services.uuid == self.serviceUUID3:
                            self.generateGen3(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, "\x01\x00")
                            continue

                        #if services.uuid == self.serviceUUIDMimic:
                            #self.generateMimic(myPeripheralConnected)
                            #characteristics = services.getCharacteristics()[0]
                            #myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, "\x01\x00")
                            #continue

    def disconnectOnePeripheralWithAddress(self, addrToDelete):
        print("\033[0;35;40m disconnectOnePeripheralWithAddress()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected > 1:
            print("Sensor we are disconnecting : ", addrToDelete)

            for myPeripheralConnected in self.listPeripheralIsConnected:

                if myPeripheralConnected.addr == addrToDelete:
                    self.listPeripheralIsConnected.remove(myPeripheralConnected)

    def disconnectOnePeripheral(self, click):
        print("\033[0;35;40m disconnectOnePeripheral()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)
        listDeviceToDisconnect = self.listPeripheralIsConnected

        for device in listDeviceToDisconnect:

            if device.addr == click:

                if numberOfPeripheralConnected > 1:

                    for myPeripheralConnected in self.listPeripheralIsConnected:

                        if myPeripheralConnected.addr == device.addr:
                            self.listPeripheralIsConnected.remove(myPeripheralConnected)

    def disconnectAllPeripheral(self):
        print("\033[0;35;40m disconnectAllPeripheral()\033[0m")

        del self.listPeripheralIsConnected[1:]

    def updateAllCapacitance(self):
        print("\033[0;35;40m updateAllCapacitance()\033[0m")

        listPeripheralUpdated = []
        numberOfPeripheralInUse = len(self.listPeripheralInUse)

        if numberOfPeripheralInUse > 0:

            for myPeripheral in self.listPeripheralInUse:

                if myPeripheral.deviceAddr != '':
                    skipThisPeripheral = False

                    for myPeripheralUpdated in listPeripheralUpdated:

                        if myPeripheral.addr == myPeripheralUpdated.deviceAddr:
                            skipThisPeripheral = True

                    if skipThisPeripheral is False:
                        listOfServices = sorted(myPeripheral.services, key=lambda services: services.hndStart)

                        for services in listOfServices:

                            if services.hndStart == services.hndEnd:
                                continue

                            if services.uuid == self.serviceUUID2:
                                self.updateGen2()
                                listPeripheralUpdated.append(myPeripheral)
                                continue

                            if services.uuid == self.serviceUUID3:
                                self.updateGen3()
                                listPeripheralUpdated.append(myPeripheral)
                                continue

                            #if services.uuid == self.serviceUUIDMimic:
                                #self.updateMimic()
                                #listPeripheralUpdated.append(myPeripheral)
                                #continue

    def updateOneCapacitance(self):
        print("\033[0;35;40m updateOneCapacitance()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected == 1:

            for myPeripheral in self.listPeripheralIsConnected:
                listOfServices = sorted(myPeripheral.services, key=lambda services: services.hndStart)

                for services in listOfServices:

                    if services.uuid == self.serviceUUID2:
                        self.updateGen2(myPeripheral)

                    elif services.uuid == self.serviceUUID3:
                        self.updateGen3(myPeripheral)

                    #elif services.uuid == self.serviceUUIDMimic:
                        #self.updateMimic(myPeripheral)

    """

    ////////////////////////////////////////////////////////////////////////////////////////////

     Functions : Discover/Generate/Update Services & Characteristics, and Wait for notifications

    ////////////////////////////////////////////////////////////////////////////////////////////

    """

    def generateGen2(self, peripheral):
        print("\033[0;35;40m generateGen2()\033[0m")

        # We create a newSensor with the address
        newSensor = StretchSensePeripheral()
        newSensor.addr = peripheral.addr
        newSensor.uuid = self.serviceUUID2
        newSensor.value = 0
        newSensor.gen = 2
        newSensor.channelNumber = 0

        self.listPeripheralIsConnected.append(newSensor)

    def generateGen3(self, peripheral):
        print("\033[0;35;40m generateGen3()\033[0m")

        # We create ten newSensor with the address
        newSensor1 = StretchSensePeripheral()
        newSensor1.addr = peripheral.addr
        newSensor1.uuid = self.serviceUUID3
        newSensor1.value = 0
        newSensor1.gen = 3
        newSensor1.channelNumber = 0

        newSensor2 = StretchSensePeripheral()
        newSensor2.addr = peripheral.addr
        newSensor2.uuid = self.serviceUUID3
        newSensor2.value = 0
        newSensor2.gen = 3
        newSensor2.channelNumber = 1

        newSensor3 = StretchSensePeripheral()
        newSensor3.addr = peripheral.addr
        newSensor3.uuid = self.serviceUUID3
        newSensor3.value = 0
        newSensor3.gen = 3
        newSensor3.channelNumber = 2

        newSensor4 = StretchSensePeripheral()
        newSensor4.addr = peripheral.addr
        newSensor4.uuid = self.serviceUUID3
        newSensor4.value = 0
        newSensor4.gen = 3
        newSensor4.channelNumber = 3

        newSensor5 = StretchSensePeripheral()
        newSensor5.addr = peripheral.addr
        newSensor5.uuid = self.serviceUUID3
        newSensor5.value = 0
        newSensor5.gen = 3
        newSensor5.channelNumber = 4

        newSensor6 = StretchSensePeripheral()
        newSensor6.addr = peripheral.addr
        newSensor6.uuid = self.serviceUUID3
        newSensor6.value = 0
        newSensor6.gen = 3
        newSensor6.channelNumber = 5

        newSensor7 = StretchSensePeripheral()
        newSensor7.addr = peripheral.addr
        newSensor7.uuid = self.serviceUUID3
        newSensor7.value = 0
        newSensor7.gen = 3
        newSensor7.channelNumber = 6

        newSensor8 = StretchSensePeripheral()
        newSensor8.addr = peripheral.addr
        newSensor8.uuid = self.serviceUUID3
        newSensor8.value = 0
        newSensor8.gen = 3
        newSensor8.channelNumber = 7

        newSensor9 = StretchSensePeripheral()
        newSensor9.addr = peripheral.addr
        newSensor9.uuid = self.serviceUUID3
        newSensor9.value = 0
        newSensor9.gen = 3
        newSensor9.channelNumber = 8

        newSensor10 = StretchSensePeripheral()
        newSensor10.addr = peripheral.addr
        newSensor10.uuid = self.serviceUUID3
        newSensor10.value = 0
        newSensor10.gen = 3
        newSensor10.channelNumber = 9

        self.listPeripheralIsConnected.append(newSensor1)
        self.listPeripheralIsConnected.append(newSensor2)
        self.listPeripheralIsConnected.append(newSensor3)
        self.listPeripheralIsConnected.append(newSensor4)
        self.listPeripheralIsConnected.append(newSensor5)
        self.listPeripheralIsConnected.append(newSensor6)
        self.listPeripheralIsConnected.append(newSensor7)
        self.listPeripheralIsConnected.append(newSensor8)
        self.listPeripheralIsConnected.append(newSensor9)
        self.listPeripheralIsConnected.append(newSensor10)

    def generateMimic(self, peripheral):
        print("\033[0;35;40m generateMimic()\033[0m")

        # We create twenty newSensor with the address
        newSensor1 = StretchSensePeripheral()
        newSensor1.uuid = peripheral.addr
        newSensor1.uuid = self.serviceUUIDMimic
        newSensor1.value = 0
        newSensor1.gen = 20
        newSensor1.channelNumber = 0

        newSensor2 = StretchSensePeripheral()
        newSensor2.uuid = peripheral.addr
        newSensor2.uuid = self.serviceUUIDMimic
        newSensor2.value = 0
        newSensor2.gen = 20
        newSensor2.channelNumber = 1

        newSensor3 = StretchSensePeripheral()
        newSensor3.uuid = peripheral.addr
        newSensor3.uuid = self.serviceUUIDMimic
        newSensor3.value = 0
        newSensor3.gen = 20
        newSensor3.channelNumber = 2

        newSensor4 = StretchSensePeripheral()
        newSensor4.uuid = peripheral.addr
        newSensor4.uuid = self.serviceUUIDMimic
        newSensor4.value = 0
        newSensor4.gen = 20
        newSensor4.channelNumber = 3

        newSensor5 = StretchSensePeripheral()
        newSensor5.uuid = peripheral.addr
        newSensor5.uuid = self.serviceUUIDMimic
        newSensor5.value = 0
        newSensor5.gen = 20
        newSensor5.channelNumber = 4

        newSensor6 = StretchSensePeripheral()
        newSensor6.uuid = peripheral.addr
        newSensor6.uuid = self.serviceUUIDMimic
        newSensor6.value = 0
        newSensor6.gen = 20
        newSensor6.channelNumber = 5

        newSensor7 = StretchSensePeripheral()
        newSensor7.uuid = peripheral.addr
        newSensor7.uuid = self.serviceUUIDMimic
        newSensor7.value = 0
        newSensor7.gen = 20
        newSensor7.channelNumber = 6

        newSensor8 = StretchSensePeripheral()
        newSensor8.uuid = peripheral.addr
        newSensor8.uuid = self.serviceUUIDMimic
        newSensor8.value = 0
        newSensor8.gen = 20
        newSensor8.channelNumber = 7

        newSensor9 = StretchSensePeripheral()
        newSensor9.uuid = peripheral.addr
        newSensor9.uuid = self.serviceUUIDMimic
        newSensor9.value = 0
        newSensor9.gen = 20
        newSensor9.channelNumber = 8

        newSensor10 = StretchSensePeripheral()
        newSensor10.uuid = peripheral.addr
        newSensor10.uuid = self.serviceUUIDMimic
        newSensor10.value = 0
        newSensor10.gen = 20
        newSensor10.channelNumber = 9

        newSensor11 = StretchSensePeripheral()
        newSensor11.uuid = peripheral.addr
        newSensor11.uuid = self.serviceUUIDMimic
        newSensor11.value = 0
        newSensor11.gen = 20
        newSensor11.channelNumber = 10

        newSensor12 = StretchSensePeripheral()
        newSensor12.uuid = peripheral.addr
        newSensor12.uuid = self.serviceUUIDMimic
        newSensor12.value = 0
        newSensor12.gen = 20
        newSensor12.channelNumber = 11

        newSensor13 = StretchSensePeripheral()
        newSensor13.uuid = peripheral.addr
        newSensor13.uuid = self.serviceUUIDMimic
        newSensor13.value = 0
        newSensor13.gen = 20
        newSensor13.channelNumber = 12

        newSensor14 = StretchSensePeripheral()
        newSensor14.uuid = peripheral.addr
        newSensor14.uuid = self.serviceUUIDMimic
        newSensor14.value = 0
        newSensor14.gen = 20
        newSensor14.channelNumber = 13

        newSensor15 = StretchSensePeripheral()
        newSensor15.uuid = peripheral.addr
        newSensor15.uuid = self.serviceUUIDMimic
        newSensor15.value = 0
        newSensor15.gen = 20
        newSensor15.channelNumber = 14

        newSensor16 = StretchSensePeripheral()
        newSensor16.uuid = peripheral.addr
        newSensor16.uuid = self.serviceUUIDMimic
        newSensor16.value = 0
        newSensor16.gen = 20
        newSensor16.channelNumber = 15

        newSensor17 = StretchSensePeripheral()
        newSensor17.uuid = peripheral.addr
        newSensor17.uuid = self.serviceUUIDMimic
        newSensor17.value = 0
        newSensor17.gen = 20
        newSensor17.channelNumber = 16

        newSensor18 = StretchSensePeripheral()
        newSensor18.uuid = peripheral.addr
        newSensor18.uuid = self.serviceUUIDMimic
        newSensor18.value = 0
        newSensor18.gen = 20
        newSensor18.channelNumber = 17

        newSensor19 = StretchSensePeripheral()
        newSensor19.uuid = peripheral.addr
        newSensor19.uuid = self.serviceUUIDMimic
        newSensor19.value = 0
        newSensor19.gen = 20
        newSensor19.channelNumber = 18

        newSensor20 = StretchSensePeripheral()
        newSensor20.uuid = peripheral.addr
        newSensor20.uuid = self.serviceUUIDMimic
        newSensor20.value = 0
        newSensor20.gen = 20
        newSensor20.channelNumber = 19

        self.listPeripheralIsConnected.append(newSensor1)
        self.listPeripheralIsConnected.append(newSensor2)
        self.listPeripheralIsConnected.append(newSensor3)
        self.listPeripheralIsConnected.append(newSensor4)
        self.listPeripheralIsConnected.append(newSensor5)
        self.listPeripheralIsConnected.append(newSensor6)
        self.listPeripheralIsConnected.append(newSensor7)
        self.listPeripheralIsConnected.append(newSensor8)
        self.listPeripheralIsConnected.append(newSensor9)
        self.listPeripheralIsConnected.append(newSensor10)
        self.listPeripheralIsConnected.append(newSensor11)
        self.listPeripheralIsConnected.append(newSensor12)
        self.listPeripheralIsConnected.append(newSensor13)
        self.listPeripheralIsConnected.append(newSensor14)
        self.listPeripheralIsConnected.append(newSensor15)
        self.listPeripheralIsConnected.append(newSensor16)
        self.listPeripheralIsConnected.append(newSensor17)
        self.listPeripheralIsConnected.append(newSensor18)
        self.listPeripheralIsConnected.append(newSensor19)
        self.listPeripheralIsConnected.append(newSensor20)

    def discoverServices(self, peripheralConnected):
        print("\033[0;35;40m discoverServices()\033[0m")

        listOfServices = sorted(peripheralConnected.services, key=lambda services: services.hndStart)

        for services in listOfServices:

            if services.hndStart == services.hndEnd:
                continue

            if services.uuid == self.serviceUUID2:
                print("Peripheral is Gen2 type")

            elif services.uuid == self.serviceUUID3:
                print("Peripheral is Gen3 type")

    def discoverCharacteristics(self, servicePeripheral):
        print("\033[0;35;40m discoverCharacteristics()\033[0m")

        characteristics = servicePeripheral.getCharacteristics()

        for chars in characteristics:

            if chars.uuid == self.dataUUID2:
                handler = chars.getHandle()
                value = servicePeripheral.readCharacteristic(handler)
                decimalValue = int(binascii.b2a_hex(value), 16) / 10.0
                print("Decimal value = <%s pF>" % decimalValue)

            elif chars.uuid == self.dataUUID3:
                handler = chars.getHandle()
                value = servicePeripheral.readCharacteristic(handler)
                decimalValue = self.convertRawDataToCapacitance(value)
                print("Decimal value = %s" % decimalValue)

    def didUpdateValue(self, data, peripheral, addr):
        #print("\033[0;35;40m didUpdateValue()\033[0m")

        if peripheral.uuid == self.serviceUUID2:
            self.updateGen2WithNotifications(data, peripheral, addr)

        if peripheral.uuid == self.serviceUUID3:
            self.updateGen3WithNotifications(data, peripheral, addr)

    def updateGen2WithNotifications(self, data, peripheralConnected, addr):
        print("\033[0;35;40m updateGen2WithNotifications()\033[0m")

        numberOfPeripheralConnected = len(globalSensor)

        if numberOfPeripheralConnected >= 1:

            if peripheralConnected.addr == addr:
                decimalValue = int(binascii.b2a_hex(data), 16) / 10.0
                peripheralConnected.value = decimalValue
                #print("peripheralConnected.value = ", peripheralConnected.value)

    def updateGen2(self):
        print("\033[0;35;40m updateGen2()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 1:

            for myPeripheral in self.listPeripheralInUse:

                for myPeripheralConnected in self.listPeripheralIsConnected:

                    if (myPeripheralConnected.gen == 2) & (myPeripheralConnected.addr == myPeripheral.addr):
                        characteristics = myPeripheral.getCharacteristics()

                        for chars in characteristics:

                            if chars.uuid == self.dataUUID2:
                                handler = chars.getHandle()
                                value = myPeripheral.readCharacteristic(handler)
                                decimalValue = int(binascii.b2a_hex(value), 16) / 10.0
                                myPeripheralConnected.value = decimalValue
                                #print("myPeripheralConnected.value = ", myPeripheralConnected.value)

    def updateGen3WithNotifications(self, data, peripheralConnected, addr):
        #print("\033[0;35;40m updateGen3WithNotifications()\033[0m")

        numberOfPeripheralConnected = len(globalSensor)

        if numberOfPeripheralConnected >= 10:

            if peripheralConnected.addr == addr:
                decimalValue = (binascii.b2a_hex(data))
                splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 4)]

                for channel in range(0, 10, 1):

                    if peripheralConnected.channelNumber == channel:
                        peripheralConnected.value = int((splitted[channel]), 16) / 10.0
                        #print("peripheralConnected.value = ", peripheralConnected.value)
                        break

    def updateGen3(self):
        print("\033[0;35;40m updateGen3()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 10:

            for myPeripheralUsed in self.listPeripheralInUse:

                for myPeripheral in self.listPeripheralInUse:

                    for myPeripheralConnected in self.listPeripheralIsConnected:

                        if (myPeripheralConnected.gen == 3) & (myPeripheralConnected.addr == myPeripheral.deviceAddr):
                            characteristics = myPeripheral.getCharacteristics()

                            for chars in characteristics:

                                if chars.uuid == self.dataUUID3:
                                    handler = chars.getHandle()
                                    value = myPeripheral.readCharacteristic(handler)
                                    decimalValue = (binascii.b2a_hex(value))
                                    splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 4)]

                                    for channel in range(0, 10, 1):

                                        if channel == myPeripheralConnected.channelNumber:
                                            myPeripheralConnected.value = int((splitted[channel]), 16) / 10.0
                                            #print("myPeripheralConnected.value = ", myPeripheralConnected.value)
                                            break
                                    break

    def updateMimic(self):
        print("\033[0;35;40m updateMimic()\033[0m")

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 20:

            for myPeripheral in self.listPeripheralInUse:

                for myPeripheralConnected in self.listPeripheralIsConnected:

                    if (myPeripheralConnected.gen == 20) & (myPeripheralConnected.addr == myPeripheral.addr):
                        characteristics = myPeripheral.getCharacteristics()

                        for chars in characteristics:

                            if chars.uuid == self.dataUUIDMimic:
                                handler = chars.getHandle()
                                value = myPeripheral.readCharacteristic(handler)
                                decimalValue = (binascii.b2a_hex(value))
                                splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 6)]

                                for channel in range(0, 20, 1):

                                    if channel == myPeripheralConnected.channelNumber:
                                        myPeripheralConnected.value = int((splitted[channel]), 16) / 10.0
                                        #print("myPeripheralConnected.value = ", myPeripheralConnected.value)
                                        break
                                break
                break

    def waitNotifications(self):
        #print("\033[0;35;40m waitNotifications()\033[0m")

        numberOfPeripheralInUse = len(self.listPeripheralInUse)
        defaultCenter = NotificationCenter()

        if numberOfPeripheralInUse >= 1:
            global globalSensor, listGlobalAddress
            globalSensor = self.listPeripheralIsConnected
            listGlobalAddress = self.listPeripheralInUse

            for myPeripheral in listGlobalAddress:

                if myPeripheral.waitForNotifications(0.001):
                    continue
                defaultCenter.postNotification("UpdateValueNotification", self.listToCsv())

    """

    /////////////////////////////////

    Functions : Lists of Peripherals

    /////////////////////////////////

    """

    def getListPeripheralAvailable(self):
        print("\033[0;35;40m getListPeripheralAvailable()\033[0m")

        return self.listPeripheralAvailable

    def getListAddrPeripheralAvailable(self):
        print("\033[0;35;40m getListAddrPeripheralAvailable()\033[0m")

        listAddr = []
        numberOfPeripheralAvailable = len(self.listPeripheralAvailable)

        if (self.listPeripheralAvailable[0].addr == ''):
            return 0

        elif numberOfPeripheralAvailable != 0:

            for i in [numberOfPeripheralAvailable - 1]:
                listAddr.append(self.listPeripheralAvailable[i].addr)
                print(listAddr)

        return listAddr

    def getListPeripheralIsConnected(self):
        print("\033[0;35;40m getListPeripheralIsConnected()\033[0m")

        return self.listPeripheralIsConnected

    def getListPeripheralOnceConnected(self):
        print("\033[0;35;40m getListPeripheralOnceConnected()\033[0m")

        return self.listPeripheralIsOnceConnected

    def getListPeripheralInUse(self):
        print("\033[0;35;40m getListPeripheralInUse()\033[0m")

        return self.listPeripheralInUse

    def listToPrint(self):
        #print("\033[0;35;40m listToPrint()\033[0m")

        listToPrint = ""
        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 1:

            for myPeripheral in self.listPeripheralIsConnected:
                listToPrint += ("[%s, %s pF] ," % (myPeripheral.channelNumber, myPeripheral.value))

        print(listToPrint)

    def listToCsv(self):
        #print("\033[0;35;40m listToCsv()\033[0m")

        listToCsv = ""
        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 1:

            for myPeripheral in self.listPeripheralIsConnected:
                listToCsv += ("%s ," % myPeripheral.value)

        print(listToCsv)

    def getLastInformation(self):
        print("\033[0;35;40m getLastInformation()\033[0m")

        return self.informationFeedBack


class StretchSenseDelegate(btle.DefaultDelegate):
    #print("\033[0;35;40m StretchSenseDelegate()\033[0m")

    def __init__(self, peripheral):
        #print("\033[0;35;40m __init__().StretchSenseDelegate()\033[0m")

        btle.DefaultDelegate.__init__(self)
        self.peripheral = peripheral
        self.addr = self.peripheral.addr

    def handleNotification(self, cHandle, data):
        #print("\033[0;35;40m StretchSenseDelegateHandleNotification()\033[0m")

        for myPeripheral in globalSensor:

            if myPeripheral.addr == self.addr:
                StretchSenseAPI().didUpdateValue(data, myPeripheral, self.addr)

"""

///////////////////////////////

Global lists of values

///////////////////////////////

"""

globalSensor = [StretchSensePeripheral()]
listGlobalAddress = [StretchSensePeripheral()]


"""    Main initialisation

//////////////////////////////////////////////////////////////////////////

Main initial declaration to compile examples and files that you are using.

//////////////////////////////////////////////////////////////////////////

"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage:\n  %s <mac-address> [random]" % sys.argv[0])

    if not os.path.isfile(btle.helperExe):
        raise ImportError("Cannot find required executable '%s'" % btle.helperExe)

    devAddr = sys.argv[1]
    if len(sys.argv) == 3:
        addrType = sys.argv[2]
    else:
        addrType = btle.ADDR_TYPE_PUBLIC
    print("Connecting to: {}, address type: {}".format(devAddr, addrType))
    conn = btle.Peripheral(devAddr, addrType)
    try:
        for svc in conn.services:
            print(str(svc), ":")
            for ch in svc.getCharacteristics():
                print("    {}, hnd={}, supports {}".format(ch, hex(ch.handle), ch.propertiesToString()))
                chName = btle.AssignedNumbers.getCommonName(ch.uuid)
                if (ch.supportsRead()):
                    try:
                        print("    ->", repr(ch.read()))
                    except btle.BTLEException as e:
                        print("    ->", e)

    finally:
        conn.disconnect()