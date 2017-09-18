#!/usr/bin/env python3

"""

    - Website : https://www.stretchsense.com

    - Important : This StretchSense Library has been designed to enable the connection of one or more "StretchSense Sensor" and "StretchSense IC Boards" to your Raspberry Pi

    - Author : Louis Germain

    - Copyright : 2017 StretchSense

    - Date : 26/07/2017

    - Version : 1.0.0

"""

from __future__ import print_function
import argparse
import binascii
import time
import os
import sys
import RPi.GPIO as GPIO
import spidev
from threading import Timer, Lock
from bluepy import btle


class RepeatedTimer(object):
    #print("RepeatedTimer()")

    """
    Class used to create a timer which repeat every defined interval.

    :param object: int, function
        int : timeout

        function : is the function that you want to repeat (should be written as lambda: "function")

    :returns:

        timer
            Returns a timer which start when the function is called, you should do "timer.stop" to terminate it

    """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


"""

Board Configuration Raspberry Pi 3 B+ SPI0:

NSS = 24
SCK = 23
MISO = 21
MOSI = 19

Board Configuration Raspberry Pi 3 B+ SPI1:

NSS = 26
SCK = 40
MISO = 35
MOSI = 38

"""
# GPIO Layout configuration

GPIOLAYOUT = GPIO.BOARD
#GPIOLAYOUT = GPIO.BCM

# Set up the SPI pattern from the GPIO LAYOUT

if (GPIOLAYOUT == GPIO.BOARD):
    CE_PIN0 = 24
    CE_PIN1 = 26
    INTERRUPT_PIN = 13
    TRIGGER_PIN = 15
elif (GPIOLAYOUT == GPIO.BCM):
    CE_PIN0 = 10
    CE_PIN1 = 11
    INTERRUPT_PIN = 2
    TRIGGER_PIN = 3

# GPIO & SPI Pin Configuration

GPIO.setmode(GPIOLAYOUT)
GPIO.setwarnings(False)
SPI0 = 0
SPI1 = 1                    # SPI1 still in developpment

# Data Package options

DATA = 0x00
CONFIG = 0x01

# Output Data Rate

RATE_OFF = 0x00
RATE_25HZ = 0x01
RATE_50HZ = 0x02
RATE_100HZ = 0x03
RATE_166HZ = 0x04
RATE_200HZ = 0x05
RATE_250HZ = 0x06
RATE_500HZ = 0x07
RATE_1KHZ = 0x08

# Interrupt Mode

INTERRUPT_DISABLED = 0x00
INTERRUPT_ENABLED = 0x01

# Trigger Mode

TRIGGER_DISABLED = 0x00
TRIGGER_ENABLED = 0x01

# Filter Mode

FILTER_0PT = 0x00
FILTER_1PT = 0x01
FILTER_3PT = 0x03
FILTER_7PT = 0x07
FILTER_15PT = 0x0F
FILTER_31PT = 0x1F
FILTER_63PT = 0x3F
FILTER_127PT = 0x7F
FILTER_255PT = 0xFF

# Resolution Mode

RESOLUTION_1pF = 0x00
RESOLUTION_100fF = 0x01
RESOLUTION_10fF = 0x02
RESOLUTION_1fF = 0x03

# Config Transfer

PADDING = 0x00

# Configuration Setup

ODR_MODE = RATE_50HZ
INTERRUPT_MODE = INTERRUPT_DISABLED
TRIGGER_MODE = TRIGGER_DISABLED
FILTER_MODE = FILTER_1PT
RESOLUTION_MODE = RESOLUTION_100fF


"""
StretchSense Classes & generators for the different type of sensors.

"""


class StretchSensePeripheral:
    #print("\033[0;35;40m StretchSensePeripheral()\033[0m")

    """
    Class which create a StretchSense peripheral with all the argument that can be used.

    :param addr: string:
        Contains the address of the device : "xx:xx:xx:xx:xx".

    :param uuid: string:
        Contains the UUID of the device "xxxxxxxx-7374-7265-7563-6873656e7365".

    :param value: int:
        Contains the value of the device in hexadecimal.

    :param channelNumber: int:
        For devices with multiple channels, contains the number of the channel.

    :param gen: string:
        This number is the generation of the device.

    :param color: string:
        This gives the device a color to use when displayed.

    """

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

        # Generation of the circuit, we initialize it at a Generation 2 which the common One-Channel sensor
        self.gen = ''

        # Background color of the circuit
        self.color = ''


class StretchSenseAPI():
    #print("\033[0;35;40m StretchSenseAPI()\033[0m")

    # This is the list of peripherals we are using for the SPI

    listPeripheralSpi = [StretchSensePeripheral()]

    # This is the list of peripherals we are using to connect to the BLE

    listPeripheralInUse = [btle.Peripheral()]

    # This is the list of StretchSense Bluetooth peripherals detected by the Raspberry Pi during a scan event

    listPeripheralAvailable = [StretchSensePeripheral()]

    # This is the list of StretchSense Bluetooth peripherals which are connected to the Raspberry Pi after being scanned

    listPeripheralIsConnected = [StretchSensePeripheral()]

    # This is the list of StretchSense Bluetooth peripherals which are saved to the Raspberry Pi after being connected once

    listPeripheralIsOnceConnected = [StretchSensePeripheral()]

    """

    Variables : Services & Characteristics UUID

    """

    # The name we use to filter BLE scan results and find only StretchSense's sensors
    deviceName = 'StretchSense'
    takoName = 'StretchSense_Tako'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense sensors Gen 3
    serviceUUID3 = '00001701-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense sensors Gen 3
    dataUUID3 = '00001702-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense sensors Gen 2
    serviceUUID2 = '00001501-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense sensors Gen 2
    dataUUID2 = '00001502-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense circuit 10TT
    serviceUUID10TT = '00601001-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense circuit 10TT
    dataUUID10TT = '00601002-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense circuit Tako
    serviceUUIDTakoLeft = '00009601-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense circuit Tako
    dataUUIDTakoLeft0 = '00009602-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft1 = '00009607-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft2 = '00009608-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft3 = '00009609-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft4 = '00009610-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft5 = '00009611-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft6 = '00009612-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft7 = '00009613-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft8 = '00009614-7374-7265-7563-6873656e7365'
    dataUUIDTakoLeft9 = '00009615-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense circuit Tako
    serviceUUIDTakoRight = '00009701-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense circuit Tako
    dataUUIDTakoRight0 = '00009702-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight1 = '00009707-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight2 = '00009708-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight3 = '00009709-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight4 = '00009710-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight5 = '00009711-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight6 = '00009712-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight7 = '00009713-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight8 = '00009714-7374-7265-7563-6873656e7365'
    dataUUIDTakoRight9 = '00009715-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense circuit Tako
    serviceUUIDTakoFront = '00009801-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense circuit Tako
    dataUUIDTakoFront0 = '00009802-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront1 = '00009807-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront2 = '00009808-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront3 = '00009809-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront4 = '00009810-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront5 = '00009811-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront6 = '00009812-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront7 = '00009813-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront8 = '00009814-7374-7265-7563-6873656e7365'
    dataUUIDTakoFront9 = '00009815-7374-7265-7563-6873656e7365'

    # The UUID used to filter Bluetooth scan results and find the services from StretchSense circuit Tako
    serviceUUIDTakoBack = '00009901-7374-7265-7563-6873656e7365'
    # The UUID used to filter the device characteristics and find the "data characteristic" from StretchSense circuit Tako
    dataUUIDTakoBack0 = '00009902-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack1 = '00009907-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack2 = '00009908-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack3 = '00009909-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack4 = '00009910-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack5 = '00009911-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack6 = '00009912-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack7 = '00009913-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack8 = '00009914-7374-7265-7563-6873656e7365'
    dataUUIDTakoBack9 = '00009915-7374-7265-7563-6873656e7365'

    """

    Variables : Set sensors & info

    """
    # Number of data samples within the filtering array

    numberOfSample = 30

    # Initialisation value of the sampling time value (SamplingTime = (value +1)*40ms)

    samplingTimeNumber = 0

    # Sized of the filter based on the number of samples

    filteringNumber = 0

    """

    Bluepy buffer Scanning class.

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

    Serial Peripheral Interface Functions

    """

    def spi_generateTenChannel(self):
        #print("\033[0;35;40m spi_generateTenChannel()\033[0m")

        """
        This function generate ten peripheral type StretchSensePeripheral used for the SPI.

        """

        newSensor1 = StretchSensePeripheral()
        newSensor1.addr = "SPI0"
        newSensor1.uuid = self.serviceUUID3
        newSensor1.value = 0
        newSensor1.gen = 3
        newSensor1.channelNumber = 0

        newSensor2 = StretchSensePeripheral()
        newSensor2.addr = "SPI0"
        newSensor2.uuid = self.serviceUUID3
        newSensor2.value = 0
        newSensor2.gen = 3
        newSensor2.channelNumber = 1

        newSensor3 = StretchSensePeripheral()
        newSensor3.addr = "SPI0"
        newSensor3.uuid = self.serviceUUID3
        newSensor3.value = 0
        newSensor3.gen = 3
        newSensor3.channelNumber = 2

        newSensor4 = StretchSensePeripheral()
        newSensor4.addr = "SPI0"
        newSensor4.uuid = self.serviceUUID3
        newSensor4.value = 0
        newSensor4.gen = 3
        newSensor4.channelNumber = 3

        newSensor5 = StretchSensePeripheral()
        newSensor5.addr = "SPI0"
        newSensor5.uuid = self.serviceUUID3
        newSensor5.value = 0
        newSensor5.gen = 3
        newSensor5.channelNumber = 4

        newSensor6 = StretchSensePeripheral()
        newSensor6.addr = "SPI0"
        newSensor6.uuid = self.serviceUUID3
        newSensor6.value = 0
        newSensor6.gen = 3
        newSensor6.channelNumber = 5

        newSensor7 = StretchSensePeripheral()
        newSensor7.addr = "SPI0"
        newSensor7.uuid = self.serviceUUID3
        newSensor7.value = 0
        newSensor7.gen = 3
        newSensor7.channelNumber = 6

        newSensor8 = StretchSensePeripheral()
        newSensor8.addr = "SPI0"
        newSensor8.uuid = self.serviceUUID3
        newSensor8.value = 0
        newSensor8.gen = 3
        newSensor8.channelNumber = 7

        newSensor9 = StretchSensePeripheral()
        newSensor9.addr = "SPI0"
        newSensor9.uuid = self.serviceUUID3
        newSensor9.value = 0
        newSensor9.gen = 3
        newSensor9.channelNumber = 8

        newSensor10 = StretchSensePeripheral()
        newSensor10.addr = "SPI0"
        newSensor10.uuid = self.serviceUUID3
        newSensor10.value = 0
        newSensor10.gen = 3
        newSensor10.channelNumber = 9

        self.listPeripheralSpi.append(newSensor1)
        self.listPeripheralSpi.append(newSensor2)
        self.listPeripheralSpi.append(newSensor3)
        self.listPeripheralSpi.append(newSensor4)
        self.listPeripheralSpi.append(newSensor5)
        self.listPeripheralSpi.append(newSensor6)
        self.listPeripheralSpi.append(newSensor7)
        self.listPeripheralSpi.append(newSensor8)
        self.listPeripheralSpi.append(newSensor9)
        self.listPeripheralSpi.append(newSensor10)

    def spi_setup(self):
        #print("\033[0;33;40m spi_setup()\033[0m")

        """

        Start the setup of the SPI communication.

        """
        # Creating a new setup requires get rid of the old one
        del self.listPeripheralSpi[0:]

        # Initialise SPI & GPIO ports
        self.myDevice = spidev.SpiDev()
        self.myDevice.close()
        self.myDevice.open(0, SPI0)
        self.myDevice.max_speed_hz = 1000
        self.myDevice.mode = 1
        self.myDevice.lsbfirst = False

        self.capacitanceScalingFactor = 100
        self.rawData = [0] * 20
        self.spi_generateTenChannel()

        # Initialise the data ready and chip enable pins
        GPIO.setup(INTERRUPT_PIN, GPIO.IN)
        GPIO.setup(CE_PIN0, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(TRIGGER_PIN, GPIO.OUT)

        # Configure 16FGV1.0
        self.spi_writeConfiguration()

        # Give the circuit the time to set up
        time.sleep(0.01)

        # Get capacitance scaling factor
        self.capacitanceScalingFactor = self.spi_getCapacitanceScalingFactor(RESOLUTION_MODE)

    def spi_mode(self):
        #print("spi_mode()")

        """

        This function is called before using the SPI transmission, it verify which mode we are using.

        """
        if (INTERRUPT_MODE == INTERRUPT_DISABLED & TRIGGER_MODE == TRIGGER_DISABLED):
            self.spi_continuousModeCapacitance()
        elif (INTERRUPT_MODE == INTERRUPT_ENABLED & TRIGGER_MODE == TRIGGER_DISABLED):
            self.spi_continuousModeCapacitance()
        elif (INTERRUPT_MODE == INTERRUPT_DISABLED & TRIGGER_MODE == TRIGGER_ENABLED):
            self.spi_triggerModeCapacitance()
        else:
            pass

    def spi_triggerModeCapacitance(self):
        #print("\033[0;35;40m spi_triggerModeCapacitance()\033[0m")

        """

        When TRIGGER is enable we use this SPI function.

        """

        # Trigger a sample to begin
        GPIO.output(TRIGGER_PIN, GPIO.HIGH)
        GPIO.output(TRIGGER_PIN, GPIO.LOW)

        # Allow the circuit to start a sample

        time.sleep(0.1)

        # Read the sensor data
        self.readData = self.spi_readCapacitance()

        # Convert the raw data to capacitance
        for i in range(10):
            self.spi_extractCapacitance(self.readData, i)

    def spi_continuousModeCapacitance(self):
        #print("\033[0;35;40m spi_continuousModeCapacitance()\033[0m")

        """

        When INTERRUPT is enable or in continuous mode we use this SPI function.

        """

        # Check if the interrupt mode is enabled (in configuration)
        if (INTERRUPT_MODE == INTERRUPT_ENABLED):
            # Don't do anything until the interrupt goes low
            while(GPIO.input(INTERRUPT_PIN) == GPIO.HIGH):
                pass

        self.readData = self.spi_readCapacitance()

        # Convert the raw data to capacitance
        for i in range(10):
            self.spi_extractCapacitance(self.readData, i)

        # Wait for the next data packet to start sampling
        if(INTERRUPT_MODE == INTERRUPT_ENABLED):
            # Don't do anything until the interruptcoes high
            while(GPIO.input(INTERRUPT_PIN) == GPIO.LOW):
                pass

    def spi_writeConfiguration(self):
        #print("\033[0;35;40m spi_writeConfiguration()\033[0m")

        """

        Function called in spi_setup() to write the configuration on the SPI bus.

        """

    # 16FGV1.0 requires a configuration package to start streaming the data

        # Set the chip select to low to select device
        GPIO.output(CE_PIN0, GPIO.LOW)

        # Select configure package and sets it
        self.myDevice.xfer2([CONFIG, ODR_MODE, INTERRUPT_MODE, TRIGGER_MODE, FILTER_MODE, RESOLUTION_MODE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # Take the chip select to high to de-select
        GPIO.output(CE_PIN0, GPIO.HIGH)

    def spi_readCapacitance(self):
        #print("\033[0;35;40m spi_readCapacitance()\033[0m")

        """

        Function which read the capacitance in hexadecimal in the SPI bus.

        :returns: int :
            raw sensing from the 16FGV1.0

        """

    # 16FGV1.0 transmits data in the form of 10, 16bit capacitance values

        # Set the chip select to low to select the device
        GPIO.output(CE_PIN0, GPIO.LOW)

        # Select Data package to return values
        raw = self.myDevice.xfer2([DATA, PADDING, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        del raw[:2]
        return raw

        #Take the chip select to high to de-select
        GPIO.output(CE_PIN0, GPIO.HIGH)

    def spi_getCapacitanceScalingFactor(self, resolutionConfig):
        #print("\033[0;33;40m spi_getCapacitanceScalingFactor()\033[0m")

        """

        The 16FGV1.0 has an adjustable LSB resolution this function scales raw data to capacitance based on
        the configuration.

        :param resolutionConfig: int :
            Resolution set on the SPI bus during spi_writeConfiguration.

        :returns: int :
            The scale of the resolution.

        """

        if resolutionConfig == RESOLUTION_1pF:
            return 1

        elif resolutionConfig == RESOLUTION_100fF:
            return 10

        elif resolutionConfig == RESOLUTION_10fF:
            return 100

        elif resolutionConfig == RESOLUTION_1fF:
            return 1000

        return 1

    def spi_extractCapacitance(self, raw, channel):
        #print("\033[0;35;40m spi_extractCapacitance()\033[0m")

        """

        Does the conversion of the raw value received by the 16FGV1.0 into a decimal value.

        :param raw: int :
            Raw is the raw value that we read on the SPI bus.
        :param channel: int :
            Number from 0 to 9 corresponding of the channel number to convert the raw value.

        """

        capacitance = 0.0
        numberOfSpiPeripheral = len(self.listPeripheralSpi)
        if numberOfSpiPeripheral > 0:

            for myPeripheral in self.listPeripheralSpi:

                if channel == myPeripheral.channelNumber:
                    capacitance = raw[2 * channel] * 256 + raw[2 * channel + 1]
                    capacitance /= self.capacitanceScalingFactor
                    myPeripheral.value = capacitance
                    #print("MainmyPeripheral.value = ", myPeripheral.value)

    def spi_listToCsv(self):
        #print("\033[0;35;40m spi_listToCsv()\033[0m")

        """

        Display the values in a csv format in the terminal.

        """

        listToCsv = ""
        numberOfSpiPeripheralConnected = len(self.listPeripheralSpi) - 1

        if numberOfSpiPeripheralConnected > 0:

            for myPeripheral in self.listPeripheralSpi:
                listToCsv += ("%s ," % myPeripheral.value)

        print("\n")
        print(listToCsv)

    def spi_getValuesCsv(self):
        #print("\033[0;35;40m spi_getValuesCsv()\033[0m")

        """

        Return the values in a csv format.

        :returns: string :
            16FGV1.0 values in a csv format.

        """

        listToReturn = ""
        numberOfSpiPeripheralConnected = len(self.listPeripheralSpi) - 1

        if numberOfSpiPeripheralConnected > 0:

            for myPeripheral in self.listPeripheralSpi:
                listToReturn += ("%s ," % myPeripheral.value)

        return listToReturn

    def spi_getListPeripheral(self):
        #print("\033[0;35;40m spi_getListPeripheral()\033[0m")

        """

        Return a list of all peripheral created by spi_generateTenChannel().

        :returns: list :
            List containing all the information of each SPI peripheral connected.

        """

        return self.listPeripheralSpi

    def spi_close(self):
        #print("\033[0;35;40m spi_close()\033[0m")

        """

        Close the SPI transmission.

        """

        self.myDevice.close()

    """

    Functions : Scan, Print, Connect/Disconnect & Update

    """

    def ble_printAllPeripheralsAvailable(self):
        #print("\033[0;35;40m ble_printAllPeripheralsAvailable()\033[0m")

        """

        Display all the StretchSense's device addresses available around.


        """

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1

        if (numberOfPeripheralAvailable == 0):
            return print("No devices available")

        elif numberOfPeripheralAvailable >= 1:

            print("Number of StretchSense devices detected : ", numberOfPeripheralAvailable)

            for myPeripheralAvailable in self.listPeripheralAvailable:

                if myPeripheralAvailable.addr != '':
                    print("StretchSense device : %s\n" % (myPeripheralAvailable.addr))

    def ble_printAllPeripheralsConnected(self):
        #print("\033[0;35;40m ble_printAllPeripheralsConnected()\033[0m")

        """
        Display all the StretchSense's device addresses connected.

        """

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected) - 1

        if (numberOfPeripheralConnected == 0):
            return print("No sensors connected")

        elif numberOfPeripheralConnected >= 1:

            for myPeripheralConnected in self.listPeripheralIsConnected:

                if myPeripheralConnected.addr != '':
                    print("StretchSense Sensor Connected : %s\n" % (myPeripheralConnected.addr))

    def ble_scanning(self, scanTime):
        #print("\033[0;35;40m ble_scanning()\033[0m")

        """

        Scan for StretchSense devices in the area and store them in listPeripheralAvailable.

        :param scanTime: int :
            Time to scan for.

        """

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
        self.listPeripheralInUse = []

        for devices in devicesAvailable:
            deviceAlreadyInTheList = False

            for (sdid, desc, val) in devices.getScanData():
                if (val == StretchSenseAPI.deviceName) or (val == StretchSenseAPI.takoName):

                    for myDeviceInTheList in self.listPeripheralAvailable:

                        if (myDeviceInTheList.addr == devices.addr):
                            deviceAlreadyInTheList = True

                    if deviceAlreadyInTheList is False:
                        self.listPeripheralAvailable.append(devices)

    def ble_connectOnePeripheral(self, myDeviceAddr):
        #print("\033[0;35;40m ble_connectOnePeripheral()\033[0m")

        """

        Connect one StretchSense device which is available using its address, generate one or more
        peripherals as StretchSensePeripheral and store them into listPeripheralIsConnected.
        The peripheral is also stored in listPeripheralInUse.

        :param myDeviceAddr: string :
            Address of the device that you want to connect.

        """

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1

        if (len(self.listPeripheralIsConnected) - 1) > 0:
            pass
        else:
            self.listPeripheralIsConnected = []

        if numberOfPeripheralAvailable > 0:
            for myPeripheralAvailable in self.listPeripheralAvailable:
                if (myPeripheralAvailable.addr == myDeviceAddr):

                    #print('Address we are trying to connect to : ', myPeripheralAvailable.addr)
                    myPeripheralConnected = btle.Peripheral(myPeripheralAvailable)
                    myPeripheralConnected.setDelegate(StretchSenseDelegate(myPeripheralConnected))
                    myPeripheralConnected.deviceAddr = myDeviceAddr
                    self.listPeripheralInUse.append(myPeripheralConnected)
                    listOfServices = sorted(myPeripheralConnected.services, key=lambda services: services.hndStart)

                    for services in listOfServices:

                        if services.hndStart == services.hndEnd:
                            continue

                        if services.uuid == self.serviceUUID2:
                            myPeripheralConnected.gen = "2"
                            myPeripheralConnected.uuid = self.serviceUUID2
                            self.ble_generateOneChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, b"\x01\x00")
                            continue

                        if services.uuid == self.serviceUUID3:
                            myPeripheralConnected.gen = "3"
                            myPeripheralConnected.uuid = self.serviceUUID3
                            self.ble_generateTenChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, b"\x01\x00")
                            continue

                        if services.uuid == self.serviceUUID10TT:
                            myPeripheralConnected.gen = "10TT"
                            myPeripheralConnected.uuid = self.serviceUUID10TT
                            self.ble_generateTenChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUID10TT:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoLeft):
                            myPeripheralConnected.gen = "TakoLeft"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoLeft
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoLeft0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoRight):
                            myPeripheralConnected.gen = "TakoRight"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoRight
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoRight0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoFront):
                            myPeripheralConnected.gen = "TakoFront"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoFront
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoFront0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoBack):
                            myPeripheralConnected.gen = "TakoBack"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoBack
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoBack0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

    def ble_connectAllPeripheral(self):
        #print("\033[0;35;40m ble_connectAllPeripheral()\033[0m")

        """

        Connect all StretchSense devices which are available using their addresses, generate the
        peripherals as StretchSensePeripheral and store them into listPeripheralIsConnected.
        Peripherals are also stored in listPeripheralInUse.

        """

        numberOfPeripheralAvailable = len(self.listPeripheralAvailable) - 1
        self.listPeripheralIsConnected = []
        self.listPeripheralInUse = []

        if numberOfPeripheralAvailable > 0:

            for myPeripheralAvailable in self.listPeripheralAvailable:

                if myPeripheralAvailable.addr != '':
                    #print('Address we are trying to connect to : ', myPeripheralAvailable.addr)
                    myPeripheralConnected = btle.Peripheral(myPeripheralAvailable)
                    myPeripheralConnected.setDelegate(StretchSenseDelegate(myPeripheralConnected))
                    myPeripheralConnected.deviceAddr = myPeripheralAvailable.addr
                    self.listPeripheralInUse.append(myPeripheralConnected)
                    listOfServices = sorted(myPeripheralConnected.services, key=lambda services: services.hndStart)

                    for services in listOfServices:
                        if services.hndStart == services.hndEnd:
                            continue

                        if services.uuid == self.serviceUUID2:
                            myPeripheralConnected.gen = '2'
                            myPeripheralConnected.uuid = self.serviceUUID2
                            self.ble_generateOneChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, b"\x01\x00")
                            continue

                        if services.uuid == self.serviceUUID3:
                            myPeripheralConnected.gen = '3'
                            myPeripheralConnected.uuid = self.serviceUUID3
                            self.ble_generateTenChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, b"\x01\x00")
                            continue

                        if services.uuid == self.serviceUUID10TT:
                            myPeripheralConnected.gen = '10TT'
                            myPeripheralConnected.uuid = self.serviceUUID10TT
                            self.ble_generateTenChannel(myPeripheralConnected)
                            characteristics = services.getCharacteristics()[0]
                            myPeripheralConnected.writeCharacteristic(characteristics.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoLeft):
                            myPeripheralConnected.gen = "TakoLeft"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoLeft
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoLeft0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoLeft9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoRight):
                            myPeripheralConnected.gen = "TakoRight"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoRight
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoRight0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoRight9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoFront):
                            myPeripheralConnected.gen = "TakoFront"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoFront
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoFront0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoFront9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

                        if (services.uuid == self.serviceUUIDTakoBack):
                            myPeripheralConnected.gen = "TakoBack"
                            myPeripheralConnected.uuid = self.serviceUUIDTakoBack
                            self.ble_generateTako(myPeripheralConnected)
                            characteristics = services.getCharacteristics()
                            for char in characteristics:
                                if char.uuid == self.dataUUIDTakoBack0:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack1:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack2:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack3:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack4:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack5:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack6:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack7:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack8:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                                if char.uuid == self.dataUUIDTakoBack9:
                                    myPeripheralConnected.writeCharacteristic(char.valHandle + 1, b"\x01\x00")
                            continue

    def ble_disconnectOnePeripheral(self, myDeviceAddr):
        #print("\033[0;35;40m ble_disconnectOnePeripheral()\033[0m")

        """
        Disconnect one StretchSense device which is connected using its address, and remove it from
        listPeripheralIsConnected.
        The peripheral is also removed from listPeripheralInUse.

        :param myDeviceAddr: string :
            Address of the device that you want to disconnect.

        """

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected > 0:

            i = 0
            for myPeripheralConnected in self.listPeripheralIsConnected:

                if myPeripheralConnected.addr == myDeviceAddr:
                    del self.listPeripheralIsConnected[i:i + 10]
                    break
                i += 1

            for myPeripheralInUse in self.listPeripheralInUse:

                if myPeripheralInUse.addr == myDeviceAddr:
                    self.listPeripheralInUse.remove(myPeripheralInUse)
                    myPeripheralInUse.disconnect()

    def ble_disconnectAllPeripherals(self):
        #print("\033[0;35;40m ble_disconnectAllPeripherals()\033[0m")

        """

        Disconnect all StretchSense devices which are connected, and remove them from both
        listPeripheralIsConnected and listPeripheralInUse.

        """

        for myPeripheralInUse in self.listPeripheralInUse:
            myPeripheralInUse.disconnect()
        del self.listPeripheralAvailable[1:]
        del self.listPeripheralIsConnected[1:]
        del self.listPeripheralInUse[1:]

    """

     Functions : Discover/Generate/Update Services & Characteristics, and wait for notifications

    """

    def ble_generateOneChannel(self, peripheral):
        #print("\033[0;35;40m ble_generateOneChannel()\033[0m")

        """

        When a StretchSense gen2 device is connected we create a newSensor receiving the
        specifications needed.

        :param peripheral: Peripheral :
            Using the BLE Peripheral format we can convert it into a StretchSensePeripheral
            format easier to use.

        :param periphUUID: UUID :
            UUID of the StretchSense circuit

        """

        # We create a newSensor with the address
        newSensor = StretchSensePeripheral()
        newSensor.addr = peripheral.addr
        newSensor.uuid = peripheral.uuid
        newSensor.value = 0
        newSensor.gen = peripheral.gen
        newSensor.channelNumber = 0

        self.listPeripheralIsConnected.append(newSensor)

    def ble_generateTenChannel(self, peripheral):
        #print("\033[0;35;40m ble_generateTenChannel()\033[0m")

        """

        When a StretchSense gen3 device is connected we create ten newSensor receiving the
        specifications needed.

        :param peripheral: Peripheral :
            Using the BLE Peripheral format we can convert it into a StretchSensePeripheral
            format easier to use.

        """

        # We create ten newSensor with the address
        newSensor1 = StretchSensePeripheral()
        newSensor1.addr = peripheral.addr
        newSensor1.uuid = peripheral.uuid
        newSensor1.value = 0
        newSensor1.gen = peripheral.gen
        newSensor1.channelNumber = 0

        newSensor2 = StretchSensePeripheral()
        newSensor2.addr = peripheral.addr
        newSensor2.uuid = peripheral.uuid
        newSensor2.value = 0
        newSensor2.gen = peripheral.gen
        newSensor2.channelNumber = 1

        newSensor3 = StretchSensePeripheral()
        newSensor3.addr = peripheral.addr
        newSensor3.uuid = peripheral.uuid
        newSensor3.value = 0
        newSensor3.gen = peripheral.gen
        newSensor3.channelNumber = 2

        newSensor4 = StretchSensePeripheral()
        newSensor4.addr = peripheral.addr
        newSensor4.uuid = peripheral.uuid
        newSensor4.value = 0
        newSensor4.gen = peripheral.gen
        newSensor4.channelNumber = 3

        newSensor5 = StretchSensePeripheral()
        newSensor5.addr = peripheral.addr
        newSensor5.uuid = peripheral.uuid
        newSensor5.value = 0
        newSensor5.gen = peripheral.gen
        newSensor5.channelNumber = 4

        newSensor6 = StretchSensePeripheral()
        newSensor6.addr = peripheral.addr
        newSensor6.uuid = peripheral.uuid
        newSensor6.value = 0
        newSensor6.gen = peripheral.gen
        newSensor6.channelNumber = 5

        newSensor7 = StretchSensePeripheral()
        newSensor7.addr = peripheral.addr
        newSensor7.uuid = peripheral.uuid
        newSensor7.value = 0
        newSensor7.gen = peripheral.gen
        newSensor7.channelNumber = 6

        newSensor8 = StretchSensePeripheral()
        newSensor8.addr = peripheral.addr
        newSensor8.uuid = peripheral.uuid
        newSensor8.value = 0
        newSensor8.gen = peripheral.gen
        newSensor8.channelNumber = 7

        newSensor9 = StretchSensePeripheral()
        newSensor9.addr = peripheral.addr
        newSensor9.uuid = peripheral.uuid
        newSensor9.value = 0
        newSensor9.gen = peripheral.gen
        newSensor9.channelNumber = 8

        newSensor10 = StretchSensePeripheral()
        newSensor10.addr = peripheral.addr
        newSensor10.uuid = peripheral.uuid
        newSensor10.value = 0
        newSensor10.gen = peripheral.gen
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

    def ble_generateTako(self, peripheral):
        #print("\033[0;35;40m ble_generateTako()\033[0m")

        """

        When a StretchSense Tako device is connected we create ten newSensor receiving the
        specifications needed.

        :param peripheral: Peripheral :
            Using the BLE Peripheral format we can convert it into a StretchSensePeripheral
            format easier to use.

        """

        # We create 96 newSensor with the address
        newSensor1 = StretchSensePeripheral()
        newSensor1.addr = peripheral.addr
        newSensor1.uuid = peripheral.uuid
        newSensor1.value = 0
        newSensor1.gen = peripheral.gen
        newSensor1.channelNumber = 0

        newSensor2 = StretchSensePeripheral()
        newSensor2.addr = peripheral.addr
        newSensor2.uuid = peripheral.uuid
        newSensor2.value = 0
        newSensor2.gen = peripheral.gen
        newSensor2.channelNumber = 1

        newSensor3 = StretchSensePeripheral()
        newSensor3.addr = peripheral.addr
        newSensor3.uuid = peripheral.uuid
        newSensor3.value = 0
        newSensor3.gen = peripheral.gen
        newSensor3.channelNumber = 2

        newSensor4 = StretchSensePeripheral()
        newSensor4.addr = peripheral.addr
        newSensor4.uuid = peripheral.uuid
        newSensor4.value = 0
        newSensor4.gen = peripheral.gen
        newSensor4.channelNumber = 3

        newSensor5 = StretchSensePeripheral()
        newSensor5.addr = peripheral.addr
        newSensor5.uuid = peripheral.uuid
        newSensor5.value = 0
        newSensor5.gen = peripheral.gen
        newSensor5.channelNumber = 4

        newSensor6 = StretchSensePeripheral()
        newSensor6.addr = peripheral.addr
        newSensor6.uuid = peripheral.uuid
        newSensor6.value = 0
        newSensor6.gen = peripheral.gen
        newSensor6.channelNumber = 5

        newSensor7 = StretchSensePeripheral()
        newSensor7.addr = peripheral.addr
        newSensor7.uuid = peripheral.uuid
        newSensor7.value = 0
        newSensor7.gen = peripheral.gen
        newSensor7.channelNumber = 6

        newSensor8 = StretchSensePeripheral()
        newSensor8.addr = peripheral.addr
        newSensor8.uuid = peripheral.uuid
        newSensor8.value = 0
        newSensor8.gen = peripheral.gen
        newSensor8.channelNumber = 7

        newSensor9 = StretchSensePeripheral()
        newSensor9.addr = peripheral.addr
        newSensor9.uuid = peripheral.uuid
        newSensor9.value = 0
        newSensor9.gen = peripheral.gen
        newSensor9.channelNumber = 8

        newSensor10 = StretchSensePeripheral()
        newSensor10.addr = peripheral.addr
        newSensor10.uuid = peripheral.uuid
        newSensor10.value = 0
        newSensor10.gen = peripheral.gen
        newSensor10.channelNumber = 9

        newSensor11 = StretchSensePeripheral()
        newSensor11.addr = peripheral.addr
        newSensor11.uuid = peripheral.uuid
        newSensor11.value = 0
        newSensor11.gen = peripheral.gen
        newSensor11.channelNumber = 10

        newSensor12 = StretchSensePeripheral()
        newSensor12.addr = peripheral.addr
        newSensor12.uuid = peripheral.uuid
        newSensor12.value = 0
        newSensor12.gen = peripheral.gen
        newSensor12.channelNumber = 11

        newSensor13 = StretchSensePeripheral()
        newSensor13.addr = peripheral.addr
        newSensor13.uuid = peripheral.uuid
        newSensor13.value = 0
        newSensor13.gen = peripheral.gen
        newSensor13.channelNumber = 12

        newSensor14 = StretchSensePeripheral()
        newSensor14.addr = peripheral.addr
        newSensor14.uuid = peripheral.uuid
        newSensor14.value = 0
        newSensor14.gen = peripheral.gen
        newSensor14.channelNumber = 13

        newSensor15 = StretchSensePeripheral()
        newSensor15.addr = peripheral.addr
        newSensor15.uuid = peripheral.uuid
        newSensor15.value = 0
        newSensor15.gen = peripheral.gen
        newSensor15.channelNumber = 14

        newSensor16 = StretchSensePeripheral()
        newSensor16.addr = peripheral.addr
        newSensor16.uuid = peripheral.uuid
        newSensor16.value = 0
        newSensor16.gen = peripheral.gen
        newSensor16.channelNumber = 15

        newSensor17 = StretchSensePeripheral()
        newSensor17.addr = peripheral.addr
        newSensor17.uuid = peripheral.uuid
        newSensor17.value = 0
        newSensor17.gen = peripheral.gen
        newSensor17.channelNumber = 16

        newSensor18 = StretchSensePeripheral()
        newSensor18.addr = peripheral.addr
        newSensor18.uuid = peripheral.uuid
        newSensor18.value = 0
        newSensor18.gen = peripheral.gen
        newSensor18.channelNumber = 17

        newSensor19 = StretchSensePeripheral()
        newSensor19.addr = peripheral.addr
        newSensor19.uuid = peripheral.uuid
        newSensor19.value = 0
        newSensor19.gen = peripheral.gen
        newSensor19.channelNumber = 18

        newSensor20 = StretchSensePeripheral()
        newSensor20.addr = peripheral.addr
        newSensor20.uuid = peripheral.uuid
        newSensor20.value = 0
        newSensor20.gen = peripheral.gen
        newSensor20.channelNumber = 19

        newSensor21 = StretchSensePeripheral()
        newSensor21.addr = peripheral.addr
        newSensor21.uuid = peripheral.uuid
        newSensor21.value = 0
        newSensor21.gen = peripheral.gen
        newSensor21.channelNumber = 20

        newSensor22 = StretchSensePeripheral()
        newSensor22.addr = peripheral.addr
        newSensor22.uuid = peripheral.uuid
        newSensor22.value = 0
        newSensor22.gen = peripheral.gen
        newSensor22.channelNumber = 21

        newSensor23 = StretchSensePeripheral()
        newSensor23.addr = peripheral.addr
        newSensor23.uuid = peripheral.uuid
        newSensor23.value = 0
        newSensor23.gen = peripheral.gen
        newSensor23.channelNumber = 22

        newSensor24 = StretchSensePeripheral()
        newSensor24.addr = peripheral.addr
        newSensor24.uuid = peripheral.uuid
        newSensor24.value = 0
        newSensor24.gen = peripheral.gen
        newSensor24.channelNumber = 23

        newSensor25 = StretchSensePeripheral()
        newSensor25.addr = peripheral.addr
        newSensor25.uuid = peripheral.uuid
        newSensor25.value = 0
        newSensor25.gen = peripheral.gen
        newSensor25.channelNumber = 24

        newSensor26 = StretchSensePeripheral()
        newSensor26.addr = peripheral.addr
        newSensor26.uuid = peripheral.uuid
        newSensor26.value = 0
        newSensor26.gen = peripheral.gen
        newSensor26.channelNumber = 25

        newSensor27 = StretchSensePeripheral()
        newSensor27.addr = peripheral.addr
        newSensor27.uuid = peripheral.uuid
        newSensor27.value = 0
        newSensor27.gen = peripheral.gen
        newSensor27.channelNumber = 26

        newSensor28 = StretchSensePeripheral()
        newSensor28.addr = peripheral.addr
        newSensor28.uuid = peripheral.uuid
        newSensor28.value = 0
        newSensor28.gen = peripheral.gen
        newSensor28.channelNumber = 27

        newSensor29 = StretchSensePeripheral()
        newSensor29.addr = peripheral.addr
        newSensor29.uuid = peripheral.uuid
        newSensor29.value = 0
        newSensor29.gen = peripheral.gen
        newSensor29.channelNumber = 28

        newSensor30 = StretchSensePeripheral()
        newSensor30.addr = peripheral.addr
        newSensor30.uuid = peripheral.uuid
        newSensor30.value = 0
        newSensor30.gen = peripheral.gen
        newSensor30.channelNumber = 29

        newSensor31 = StretchSensePeripheral()
        newSensor31.addr = peripheral.addr
        newSensor31.uuid = peripheral.uuid
        newSensor31.value = 0
        newSensor31.gen = peripheral.gen
        newSensor31.channelNumber = 30

        newSensor32 = StretchSensePeripheral()
        newSensor32.addr = peripheral.addr
        newSensor32.uuid = peripheral.uuid
        newSensor32.value = 0
        newSensor32.gen = peripheral.gen
        newSensor32.channelNumber = 31

        newSensor33 = StretchSensePeripheral()
        newSensor33.addr = peripheral.addr
        newSensor33.uuid = peripheral.uuid
        newSensor33.value = 0
        newSensor33.gen = peripheral.gen
        newSensor33.channelNumber = 32

        newSensor34 = StretchSensePeripheral()
        newSensor34.addr = peripheral.addr
        newSensor34.uuid = peripheral.uuid
        newSensor34.value = 0
        newSensor34.gen = peripheral.gen
        newSensor34.channelNumber = 33

        newSensor35 = StretchSensePeripheral()
        newSensor35.addr = peripheral.addr
        newSensor35.uuid = peripheral.uuid
        newSensor35.value = 0
        newSensor35.gen = peripheral.gen
        newSensor35.channelNumber = 34

        newSensor36 = StretchSensePeripheral()
        newSensor36.addr = peripheral.addr
        newSensor36.uuid = peripheral.uuid
        newSensor36.value = 0
        newSensor36.gen = peripheral.gen
        newSensor36.channelNumber = 35

        newSensor37 = StretchSensePeripheral()
        newSensor37.addr = peripheral.addr
        newSensor37.uuid = peripheral.uuid
        newSensor37.value = 0
        newSensor37.gen = peripheral.gen
        newSensor37.channelNumber = 36

        newSensor38 = StretchSensePeripheral()
        newSensor38.addr = peripheral.addr
        newSensor38.uuid = peripheral.uuid
        newSensor38.value = 0
        newSensor38.gen = peripheral.gen
        newSensor38.channelNumber = 37

        newSensor39 = StretchSensePeripheral()
        newSensor39.addr = peripheral.addr
        newSensor39.uuid = peripheral.uuid
        newSensor39.value = 0
        newSensor39.gen = peripheral.gen
        newSensor39.channelNumber = 38

        newSensor40 = StretchSensePeripheral()
        newSensor40.addr = peripheral.addr
        newSensor40.uuid = peripheral.uuid
        newSensor40.value = 0
        newSensor40.gen = peripheral.gen
        newSensor40.channelNumber = 39

        newSensor41 = StretchSensePeripheral()
        newSensor41.addr = peripheral.addr
        newSensor41.uuid = peripheral.uuid
        newSensor41.value = 0
        newSensor41.gen = peripheral.gen
        newSensor41.channelNumber = 40

        newSensor42 = StretchSensePeripheral()
        newSensor42.addr = peripheral.addr
        newSensor42.uuid = peripheral.uuid
        newSensor42.value = 0
        newSensor42.gen = peripheral.gen
        newSensor42.channelNumber = 41

        newSensor43 = StretchSensePeripheral()
        newSensor43.addr = peripheral.addr
        newSensor43.uuid = peripheral.uuid
        newSensor43.value = 0
        newSensor43.gen = peripheral.gen
        newSensor43.channelNumber = 42

        newSensor44 = StretchSensePeripheral()
        newSensor44.addr = peripheral.addr
        newSensor44.uuid = peripheral.uuid
        newSensor44.value = 0
        newSensor44.gen = peripheral.gen
        newSensor44.channelNumber = 43

        newSensor45 = StretchSensePeripheral()
        newSensor45.addr = peripheral.addr
        newSensor45.uuid = peripheral.uuid
        newSensor45.value = 0
        newSensor45.gen = peripheral.gen
        newSensor45.channelNumber = 44

        newSensor46 = StretchSensePeripheral()
        newSensor46.addr = peripheral.addr
        newSensor46.uuid = peripheral.uuid
        newSensor46.value = 0
        newSensor46.gen = peripheral.gen
        newSensor46.channelNumber = 45

        newSensor47 = StretchSensePeripheral()
        newSensor47.addr = peripheral.addr
        newSensor47.uuid = peripheral.uuid
        newSensor47.value = 0
        newSensor47.gen = peripheral.gen
        newSensor47.channelNumber = 46

        newSensor48 = StretchSensePeripheral()
        newSensor48.addr = peripheral.addr
        newSensor48.uuid = peripheral.uuid
        newSensor48.value = 0
        newSensor48.gen = peripheral.gen
        newSensor48.channelNumber = 47

        newSensor49 = StretchSensePeripheral()
        newSensor49.addr = peripheral.addr
        newSensor49.uuid = peripheral.uuid
        newSensor49.value = 0
        newSensor49.gen = peripheral.gen
        newSensor49.channelNumber = 48

        newSensor50 = StretchSensePeripheral()
        newSensor50.addr = peripheral.addr
        newSensor50.uuid = peripheral.uuid
        newSensor50.value = 0
        newSensor50.gen = peripheral.gen
        newSensor50.channelNumber = 49

        newSensor51 = StretchSensePeripheral()
        newSensor51.addr = peripheral.addr
        newSensor51.uuid = peripheral.uuid
        newSensor51.value = 0
        newSensor51.gen = peripheral.gen
        newSensor51.channelNumber = 50

        newSensor52 = StretchSensePeripheral()
        newSensor52.addr = peripheral.addr
        newSensor52.uuid = peripheral.uuid
        newSensor52.value = 0
        newSensor52.gen = peripheral.gen
        newSensor52.channelNumber = 51

        newSensor53 = StretchSensePeripheral()
        newSensor53.addr = peripheral.addr
        newSensor53.uuid = peripheral.uuid
        newSensor53.value = 0
        newSensor53.gen = peripheral.gen
        newSensor53.channelNumber = 52

        newSensor54 = StretchSensePeripheral()
        newSensor54.addr = peripheral.addr
        newSensor54.uuid = peripheral.uuid
        newSensor54.value = 0
        newSensor54.gen = peripheral.gen
        newSensor54.channelNumber = 53

        newSensor55 = StretchSensePeripheral()
        newSensor55.addr = peripheral.addr
        newSensor55.uuid = peripheral.uuid
        newSensor55.value = 0
        newSensor55.gen = peripheral.gen
        newSensor55.channelNumber = 54

        newSensor56 = StretchSensePeripheral()
        newSensor56.addr = peripheral.addr
        newSensor56.uuid = peripheral.uuid
        newSensor56.value = 0
        newSensor56.gen = peripheral.gen
        newSensor56.channelNumber = 55

        newSensor57 = StretchSensePeripheral()
        newSensor57.addr = peripheral.addr
        newSensor57.uuid = peripheral.uuid
        newSensor57.value = 0
        newSensor57.gen = peripheral.gen
        newSensor57.channelNumber = 56

        newSensor58 = StretchSensePeripheral()
        newSensor58.addr = peripheral.addr
        newSensor58.uuid = peripheral.uuid
        newSensor58.value = 0
        newSensor58.gen = peripheral.gen
        newSensor58.channelNumber = 57

        newSensor59 = StretchSensePeripheral()
        newSensor59.addr = peripheral.addr
        newSensor59.uuid = peripheral.uuid
        newSensor59.value = 0
        newSensor59.gen = peripheral.gen
        newSensor59.channelNumber = 58

        newSensor60 = StretchSensePeripheral()
        newSensor60.addr = peripheral.addr
        newSensor60.uuid = peripheral.uuid
        newSensor60.value = 0
        newSensor60.gen = peripheral.gen
        newSensor60.channelNumber = 59

        newSensor61 = StretchSensePeripheral()
        newSensor61.addr = peripheral.addr
        newSensor61.uuid = peripheral.uuid
        newSensor61.value = 0
        newSensor61.gen = peripheral.gen
        newSensor61.channelNumber = 60

        newSensor62 = StretchSensePeripheral()
        newSensor62.addr = peripheral.addr
        newSensor62.uuid = peripheral.uuid
        newSensor62.value = 0
        newSensor62.gen = peripheral.gen
        newSensor62.channelNumber = 61

        newSensor63 = StretchSensePeripheral()
        newSensor63.addr = peripheral.addr
        newSensor63.uuid = peripheral.uuid
        newSensor63.value = 0
        newSensor63.gen = peripheral.gen
        newSensor63.channelNumber = 62

        newSensor64 = StretchSensePeripheral()
        newSensor64.addr = peripheral.addr
        newSensor64.uuid = peripheral.uuid
        newSensor64.value = 0
        newSensor64.gen = peripheral.gen
        newSensor64.channelNumber = 63

        newSensor65 = StretchSensePeripheral()
        newSensor65.addr = peripheral.addr
        newSensor65.uuid = peripheral.uuid
        newSensor65.value = 0
        newSensor65.gen = peripheral.gen
        newSensor65.channelNumber = 64

        newSensor66 = StretchSensePeripheral()
        newSensor66.addr = peripheral.addr
        newSensor66.uuid = peripheral.uuid
        newSensor66.value = 0
        newSensor66.gen = peripheral.gen
        newSensor66.channelNumber = 65

        newSensor67 = StretchSensePeripheral()
        newSensor67.addr = peripheral.addr
        newSensor67.uuid = peripheral.uuid
        newSensor67.value = 0
        newSensor67.gen = peripheral.gen
        newSensor67.channelNumber = 66

        newSensor68 = StretchSensePeripheral()
        newSensor68.addr = peripheral.addr
        newSensor68.uuid = peripheral.uuid
        newSensor68.value = 0
        newSensor68.gen = peripheral.gen
        newSensor68.channelNumber = 67

        newSensor69 = StretchSensePeripheral()
        newSensor69.addr = peripheral.addr
        newSensor69.uuid = peripheral.uuid
        newSensor69.value = 0
        newSensor69.gen = peripheral.gen
        newSensor69.channelNumber = 68

        newSensor70 = StretchSensePeripheral()
        newSensor70.addr = peripheral.addr
        newSensor70.uuid = peripheral.uuid
        newSensor70.value = 0
        newSensor70.gen = peripheral.gen
        newSensor70.channelNumber = 69

        newSensor71 = StretchSensePeripheral()
        newSensor71.addr = peripheral.addr
        newSensor71.uuid = peripheral.uuid
        newSensor71.value = 0
        newSensor71.gen = peripheral.gen
        newSensor71.channelNumber = 70

        newSensor72 = StretchSensePeripheral()
        newSensor72.addr = peripheral.addr
        newSensor72.uuid = peripheral.uuid
        newSensor72.value = 0
        newSensor72.gen = peripheral.gen
        newSensor72.channelNumber = 71

        newSensor73 = StretchSensePeripheral()
        newSensor73.addr = peripheral.addr
        newSensor73.uuid = peripheral.uuid
        newSensor73.value = 0
        newSensor73.gen = peripheral.gen
        newSensor73.channelNumber = 72

        newSensor74 = StretchSensePeripheral()
        newSensor74.addr = peripheral.addr
        newSensor74.uuid = peripheral.uuid
        newSensor74.value = 0
        newSensor74.gen = peripheral.gen
        newSensor74.channelNumber = 73

        newSensor75 = StretchSensePeripheral()
        newSensor75.addr = peripheral.addr
        newSensor75.uuid = peripheral.uuid
        newSensor75.value = 0
        newSensor75.gen = peripheral.gen
        newSensor75.channelNumber = 74

        newSensor76 = StretchSensePeripheral()
        newSensor76.addr = peripheral.addr
        newSensor76.uuid = peripheral.uuid
        newSensor76.value = 0
        newSensor76.gen = peripheral.gen
        newSensor76.channelNumber = 75

        newSensor77 = StretchSensePeripheral()
        newSensor77.addr = peripheral.addr
        newSensor77.uuid = peripheral.uuid
        newSensor77.value = 0
        newSensor77.gen = peripheral.gen
        newSensor77.channelNumber = 76

        newSensor78 = StretchSensePeripheral()
        newSensor78.addr = peripheral.addr
        newSensor78.uuid = peripheral.uuid
        newSensor78.value = 0
        newSensor78.gen = peripheral.gen
        newSensor78.channelNumber = 77

        newSensor79 = StretchSensePeripheral()
        newSensor79.addr = peripheral.addr
        newSensor79.uuid = peripheral.uuid
        newSensor79.value = 0
        newSensor79.gen = peripheral.gen
        newSensor79.channelNumber = 78

        newSensor80 = StretchSensePeripheral()
        newSensor80.addr = peripheral.addr
        newSensor80.uuid = peripheral.uuid
        newSensor80.value = 0
        newSensor80.gen = peripheral.gen
        newSensor80.channelNumber = 79

        newSensor81 = StretchSensePeripheral()
        newSensor81.addr = peripheral.addr
        newSensor81.uuid = peripheral.uuid
        newSensor81.value = 0
        newSensor81.gen = peripheral.gen
        newSensor81.channelNumber = 80

        newSensor82 = StretchSensePeripheral()
        newSensor82.addr = peripheral.addr
        newSensor82.uuid = peripheral.uuid
        newSensor82.value = 0
        newSensor82.gen = peripheral.gen
        newSensor82.channelNumber = 81

        newSensor83 = StretchSensePeripheral()
        newSensor83.addr = peripheral.addr
        newSensor83.uuid = peripheral.uuid
        newSensor83.value = 0
        newSensor83.gen = peripheral.gen
        newSensor83.channelNumber = 82

        newSensor84 = StretchSensePeripheral()
        newSensor84.addr = peripheral.addr
        newSensor84.uuid = peripheral.uuid
        newSensor84.value = 0
        newSensor84.gen = peripheral.gen
        newSensor84.channelNumber = 83

        newSensor85 = StretchSensePeripheral()
        newSensor85.addr = peripheral.addr
        newSensor85.uuid = peripheral.uuid
        newSensor85.value = 0
        newSensor85.gen = peripheral.gen
        newSensor85.channelNumber = 84

        newSensor86 = StretchSensePeripheral()
        newSensor86.addr = peripheral.addr
        newSensor86.uuid = peripheral.uuid
        newSensor86.value = 0
        newSensor86.gen = peripheral.gen
        newSensor86.channelNumber = 85

        newSensor87 = StretchSensePeripheral()
        newSensor87.addr = peripheral.addr
        newSensor87.uuid = peripheral.uuid
        newSensor87.value = 0
        newSensor87.gen = peripheral.gen
        newSensor87.channelNumber = 86

        newSensor88 = StretchSensePeripheral()
        newSensor88.addr = peripheral.addr
        newSensor88.uuid = peripheral.uuid
        newSensor88.value = 0
        newSensor88.gen = peripheral.gen
        newSensor88.channelNumber = 87

        newSensor89 = StretchSensePeripheral()
        newSensor89.addr = peripheral.addr
        newSensor89.uuid = peripheral.uuid
        newSensor89.value = 0
        newSensor89.gen = peripheral.gen
        newSensor89.channelNumber = 88

        newSensor90 = StretchSensePeripheral()
        newSensor90.addr = peripheral.addr
        newSensor90.uuid = peripheral.uuid
        newSensor90.value = 0
        newSensor90.gen = peripheral.gen
        newSensor90.channelNumber = 89

        newSensor91 = StretchSensePeripheral()
        newSensor91.addr = peripheral.addr
        newSensor91.uuid = peripheral.uuid
        newSensor91.value = 0
        newSensor91.gen = peripheral.gen
        newSensor91.channelNumber = 90

        newSensor92 = StretchSensePeripheral()
        newSensor92.addr = peripheral.addr
        newSensor92.uuid = peripheral.uuid
        newSensor92.value = 0
        newSensor92.gen = peripheral.gen
        newSensor92.channelNumber = 91

        newSensor93 = StretchSensePeripheral()
        newSensor93.addr = peripheral.addr
        newSensor93.uuid = peripheral.uuid
        newSensor93.value = 0
        newSensor93.gen = peripheral.gen
        newSensor93.channelNumber = 92

        newSensor94 = StretchSensePeripheral()
        newSensor94.addr = peripheral.addr
        newSensor94.uuid = peripheral.uuid
        newSensor94.value = 0
        newSensor94.gen = peripheral.gen
        newSensor94.channelNumber = 93

        newSensor95 = StretchSensePeripheral()
        newSensor95.addr = peripheral.addr
        newSensor95.uuid = peripheral.uuid
        newSensor95.value = 0
        newSensor95.gen = peripheral.gen
        newSensor95.channelNumber = 94

        newSensor96 = StretchSensePeripheral()
        newSensor96.addr = peripheral.addr
        newSensor96.uuid = peripheral.uuid
        newSensor96.value = 0
        newSensor96.gen = peripheral.gen
        newSensor96.channelNumber = 95

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
        self.listPeripheralIsConnected.append(newSensor21)
        self.listPeripheralIsConnected.append(newSensor22)
        self.listPeripheralIsConnected.append(newSensor23)
        self.listPeripheralIsConnected.append(newSensor24)
        self.listPeripheralIsConnected.append(newSensor25)
        self.listPeripheralIsConnected.append(newSensor26)
        self.listPeripheralIsConnected.append(newSensor27)
        self.listPeripheralIsConnected.append(newSensor28)
        self.listPeripheralIsConnected.append(newSensor29)
        self.listPeripheralIsConnected.append(newSensor30)
        self.listPeripheralIsConnected.append(newSensor31)
        self.listPeripheralIsConnected.append(newSensor32)
        self.listPeripheralIsConnected.append(newSensor33)
        self.listPeripheralIsConnected.append(newSensor34)
        self.listPeripheralIsConnected.append(newSensor35)
        self.listPeripheralIsConnected.append(newSensor36)
        self.listPeripheralIsConnected.append(newSensor37)
        self.listPeripheralIsConnected.append(newSensor38)
        self.listPeripheralIsConnected.append(newSensor39)
        self.listPeripheralIsConnected.append(newSensor40)
        self.listPeripheralIsConnected.append(newSensor41)
        self.listPeripheralIsConnected.append(newSensor42)
        self.listPeripheralIsConnected.append(newSensor43)
        self.listPeripheralIsConnected.append(newSensor44)
        self.listPeripheralIsConnected.append(newSensor45)
        self.listPeripheralIsConnected.append(newSensor46)
        self.listPeripheralIsConnected.append(newSensor47)
        self.listPeripheralIsConnected.append(newSensor48)
        self.listPeripheralIsConnected.append(newSensor49)
        self.listPeripheralIsConnected.append(newSensor50)
        self.listPeripheralIsConnected.append(newSensor51)
        self.listPeripheralIsConnected.append(newSensor52)
        self.listPeripheralIsConnected.append(newSensor53)
        self.listPeripheralIsConnected.append(newSensor54)
        self.listPeripheralIsConnected.append(newSensor55)
        self.listPeripheralIsConnected.append(newSensor56)
        self.listPeripheralIsConnected.append(newSensor57)
        self.listPeripheralIsConnected.append(newSensor58)
        self.listPeripheralIsConnected.append(newSensor59)
        self.listPeripheralIsConnected.append(newSensor60)
        self.listPeripheralIsConnected.append(newSensor61)
        self.listPeripheralIsConnected.append(newSensor62)
        self.listPeripheralIsConnected.append(newSensor63)
        self.listPeripheralIsConnected.append(newSensor64)
        self.listPeripheralIsConnected.append(newSensor65)
        self.listPeripheralIsConnected.append(newSensor66)
        self.listPeripheralIsConnected.append(newSensor67)
        self.listPeripheralIsConnected.append(newSensor68)
        self.listPeripheralIsConnected.append(newSensor69)
        self.listPeripheralIsConnected.append(newSensor70)
        self.listPeripheralIsConnected.append(newSensor71)
        self.listPeripheralIsConnected.append(newSensor72)
        self.listPeripheralIsConnected.append(newSensor73)
        self.listPeripheralIsConnected.append(newSensor74)
        self.listPeripheralIsConnected.append(newSensor75)
        self.listPeripheralIsConnected.append(newSensor76)
        self.listPeripheralIsConnected.append(newSensor77)
        self.listPeripheralIsConnected.append(newSensor78)
        self.listPeripheralIsConnected.append(newSensor79)
        self.listPeripheralIsConnected.append(newSensor80)
        self.listPeripheralIsConnected.append(newSensor81)
        self.listPeripheralIsConnected.append(newSensor82)
        self.listPeripheralIsConnected.append(newSensor83)
        self.listPeripheralIsConnected.append(newSensor84)
        self.listPeripheralIsConnected.append(newSensor85)
        self.listPeripheralIsConnected.append(newSensor86)
        self.listPeripheralIsConnected.append(newSensor78)
        self.listPeripheralIsConnected.append(newSensor88)
        self.listPeripheralIsConnected.append(newSensor89)
        self.listPeripheralIsConnected.append(newSensor90)
        self.listPeripheralIsConnected.append(newSensor91)
        self.listPeripheralIsConnected.append(newSensor92)
        self.listPeripheralIsConnected.append(newSensor93)
        self.listPeripheralIsConnected.append(newSensor94)
        self.listPeripheralIsConnected.append(newSensor95)
        self.listPeripheralIsConnected.append(newSensor96)

    def ble_discoverServices(self):
        #print("\033[0;35;40m ble_discoverServices()\033[0m")

        """

        Display on the terminal all the services for each StretchSense devices connected.

        """

        for myPeripheral in self.listPeripheralInUse:

            listOfServices = sorted(myPeripheral.services, key=lambda services: services.hndStart)

            for services in listOfServices:

                print(services)

    def ble_discoverCharacteristics(self):
        print("\033[0;35;40m ble_discoverCharacteristics()\033[0m")

        """
        Display on the terminal all the characteristics for each StretchSense devices connected.

        """

        for myPeripheral in self.listPeripheralInUse:

            listOfServices = sorted(myPeripheral.services, key=lambda services: services.hndStart)

            for services in listOfServices:

                characteristics = services.getCharacteristics()

                for chars in characteristics:

                    print(chars)

    def ble_updateOneChannelWithNotifications(self, data, addr):
        #print("\033[0;35;40m ble_updateOneChannelWithNotifications()\033[0m")

        """

        Update data from one or more StretchSense gen2 devices connected using BLE notifications
        and stores its value.

        :param data: UTF-8 characters :
            data transmitted by the device once a notification is detected.

        :param addr: string :
            Address of the gen2 we want to update.

        """

        numberOfPeripheralConnected = len(globalSensor)

        if numberOfPeripheralConnected >= 1:
            for myPeripheral in globalSensor:
                if myPeripheral.addr == addr:
                    decimalValue = int(binascii.b2a_hex(data), 16) / 10.0
                    myPeripheral.value = decimalValue
                    #print("myPeripheral.value = ", myPeripheral.value)

    def ble_updateOneChannel(self):
        #print("\033[0;35;40m ble_updateOneChannel()\033[0m")

        """

        Update once the value of every StretchSense gen2 devices connected without using BLE notifications.

        """

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
                                print("myPeripheralConnected.value = ", myPeripheralConnected.value)

    def ble_updateTenChannelWithNotifications(self, data, addr):
        #print("\033[0;35;40m ble_updateTenChannelWithNotifications()\033[0m")

        """

        Update data from one or more StretchSense gen3 devices connected using BLE notifications
        and stores its value.

        :param data: UTF-8 characters :
            data transmitted by the device once a notification is detected.

        :param addr: string :
            Address of the gen3 we want to update.

        """

        numberOfPeripheralConnected = len(globalSensor)

        if numberOfPeripheralConnected >= 10:
            for myPeripheral in globalSensor:
                if myPeripheral.addr == addr:
                    index = globalSensor.index(myPeripheral)

                    decimalValue = (binascii.b2a_hex(data))
                    splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 4)]
                    globalSensor[index + 0].value = int((splitted[0]), 16) / 10.0
                    globalSensor[index + 1].value = int((splitted[1]), 16) / 10.0
                    globalSensor[index + 2].value = int((splitted[2]), 16) / 10.0
                    globalSensor[index + 3].value = int((splitted[3]), 16) / 10.0
                    globalSensor[index + 4].value = int((splitted[4]), 16) / 10.0
                    globalSensor[index + 5].value = int((splitted[5]), 16) / 10.0
                    globalSensor[index + 6].value = int((splitted[6]), 16) / 10.0
                    globalSensor[index + 7].value = int((splitted[7]), 16) / 10.0
                    globalSensor[index + 8].value = int((splitted[8]), 16) / 10.0
                    globalSensor[index + 9].value = int((splitted[9]), 16) / 10.0
                    break

    def ble_updateTakoWithNotifications(self, data, handler, addr):
        #print("\033[0;35;40m ble_updateTakoWithNotifications()\033[0m")

        """

        Update data from one or more StretchSense Tako devices connected using BLE notifications
        and stores its value.

        :param data: UTF-8 characters :
            data transmitted by the device once a notification is detected.

        :param addr: string :
            Address of the Tako we want to update.

        """

        numberOfPeripheralConnected = len(globalSensor)

        if numberOfPeripheralConnected >= 96:
            for myPeripheral in globalSensor:
                if myPeripheral.addr == addr:
                    if handler == 14:
                        offset = 0
                    if handler == 17:
                        offset = 1
                    if handler == 20:
                        offset = 2
                    if handler == 23:
                        offset = 3
                    if handler == 26:
                        offset = 4
                    if handler == 29:
                        offset = 5
                    if handler == 32:
                        offset = 6
                    if handler == 35:
                        offset = 7
                    if handler == 38:
                        offset = 8
                    if handler == 41:
                        offset = 9

                    decimalValue = (binascii.b2a_hex(data))
                    splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 4)]

                    globalSensor[offset * 10 + 0].value = int((splitted[0]), 16) / 10.0
                    globalSensor[offset * 10 + 1].value = int((splitted[1]), 16) / 10.0
                    globalSensor[offset * 10 + 2].value = int((splitted[2]), 16) / 10.0
                    globalSensor[offset * 10 + 3].value = int((splitted[3]), 16) / 10.0
                    globalSensor[offset * 10 + 4].value = int((splitted[4]), 16) / 10.0
                    globalSensor[offset * 10 + 5].value = int((splitted[5]), 16) / 10.0
                    if offset == 9:
                        break
                    globalSensor[offset * 10 + 6].value = int((splitted[6]), 16) / 10.0
                    globalSensor[offset * 10 + 7].value = int((splitted[7]), 16) / 10.0
                    globalSensor[offset * 10 + 8].value = int((splitted[8]), 16) / 10.0
                    globalSensor[offset * 10 + 9].value = int((splitted[9]), 16) / 10.0
                    break

    def ble_updateTenChannel(self):
        #print("\033[0;35;40m ble_updateTenChannel()\033[0m")

        """

        Update once the value of every StretchSense gen3 devices connected without BLE using notifications.

        """

        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 10:

            for myPeripheral in self.listPeripheralInUse:

                for myPeripheralConnected in self.listPeripheralIsConnected:

                    if (myPeripheralConnected.gen == 3) & (myPeripheralConnected.addr == myPeripheral.deviceAddr):
                        characteristics = myPeripheral.getCharacteristics()

                        for chars in characteristics:

                            if chars.uuid == (self.dataUUID3 or self.dataUUID10TT):
                                handler = chars.getHandle()
                                value = myPeripheral.readCharacteristic(handler)
                                decimalValue = (binascii.b2a_hex(value))
                                splitted = [decimalValue[i:i + 4] for i in range(0, len(decimalValue), 4)]

                                for channel in range(0, 10, 1):

                                    if channel == myPeripheralConnected.channelNumber:
                                        myPeripheralConnected.value = int((splitted[channel]), 16) / 10.0
                                        print("myPeripheralConnected.value = ", myPeripheralConnected.value)
                                        break
                                break

    def ble_updateAllPeripherals(self):
        #print("\033[0;35;40m ble_updateAllPeripherals()\033[0m")

        """

        Update the value of the capacitance of each StretchSense devices which are connected.

        """

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
                                self.ble_updateOneChannel()
                                listPeripheralUpdated.append(myPeripheral)
                                continue

                            if services.uuid == self.serviceUUID3:
                                self.ble_updateTenChannel()
                                listPeripheralUpdated.append(myPeripheral)
                                continue

    def ble_waitNotifications(self):
        #print("\033[0;35;40m ble_waitNotifications()\033[0m")

        """
        When called, run into all connected devices waiting for notification from each of them
        and store the new data in their value slot.

        """

        numberOfPeripheralInUse = len(self.listPeripheralInUse)

        if numberOfPeripheralInUse > 0:

            global globalSensor
            globalSensor = self.listPeripheralIsConnected

            for myPeripheral in self.listPeripheralInUse:
                if myPeripheral.waitForNotifications(0.001):
                    continue
                self.listPeripheralIsConnected = globalSensor

    """

    Functions : Lists of Peripherals

    """

    def ble_getListPeripheralAvailable(self):
        #print("\033[0;35;40m ble_getListPeripheralAvailable()\033[0m")

        """

        Returns the list of all devices available in the area.

        :returns: [Peripheral] : List of all the devices available.

        """

        return self.listPeripheralAvailable

    def ble_getListAddrPeripheralAvailable(self):
        #print("\033[0;35;40m ble_getListAddrPeripheralAvailable()\033[0m")

        """

        Returns the list of all devices address available in the area.

        :returns: [addr] : List of all devices available addresses.

        """

        listAddr = []
        numberOfPeripheralAvailable = len(self.listPeripheralAvailable)

        if (self.listPeripheralAvailable[0].addr == ''):
            return 0

        elif numberOfPeripheralAvailable != 0:

            for i in [numberOfPeripheralAvailable - 1]:
                listAddr.append(self.listPeripheralAvailable[i].addr)
                print(listAddr)

        return listAddr

    def ble_getListPeripheralIsConnected(self):
        #print("\033[0;35;40m ble_getListPeripheralIsConnected()\033[0m")

        """

        Returns the list of all devices connected.

        :returns: [StretchSensePeripheral] : List of all devices connected.

        """

        return self.listPeripheralIsConnected

    def ble_getListPeripheralOnceConnected(self):
        #print("\033[0;35;40m ble_getListPeripheralOnceConnected()\033[0m")

        """

        Returns the list of all devices once connected.

        :returns: [StretchSensePeripheral] : List of all devices once connected.

        """

        return self.listPeripheralIsOnceConnected

    def ble_getListPeripheralInUse(self):
        #print("\033[0;35;40m ble_getListPeripheralInUse()\033[0m")

        """

        Returns the list of all devices currently in use.

        :returns: [Peripheral] : List of all devices we are using.

        """

        return self.listPeripheralInUse

    def ble_listToCsv(self):
        #print("\033[0;35;40m ble_listToCsv()\033[0m")

        """

        Displays on the terminal the values of each connected devices in a csv format.

        """

        listToCsv = ""
        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected >= 1:

            for myPeripheral in self.listPeripheralIsConnected:
                listToCsv += ("%s ," % myPeripheral.value)

        listToCsv += ("\n")
        print(listToCsv)

    def ble_getValuesCsv(self):
        #print("\033[0;35;40m ble_getValuesCsv()\033[0m")

        """

        Returns the values of each connected devices in a csv format.

        :returns: string : Values of each connected devices.

        """

        listToReturn = ""
        numberOfPeripheralConnected = len(self.listPeripheralIsConnected)

        if numberOfPeripheralConnected > 0:

            for myPeripheral in self.listPeripheralIsConnected:
                listToReturn += ("%s , " % myPeripheral.value)

        return listToReturn


"""

Class StretchSenseDelegate : Class to handle the BLE notifications

"""


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

                if myPeripheral.uuid == StretchSenseAPI.serviceUUID2:
                    StretchSenseAPI.ble_updateOneChannelWithNotifications(self, data, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUID3:
                    StretchSenseAPI.ble_updateTenChannelWithNotifications(self, data, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUID10TT:
                    StretchSenseAPI.ble_updateTenChannelWithNotifications(self, data, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUIDTakoLeft:
                    StretchSenseAPI.ble_updateTakoWithNotifications(self, data, cHandle, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUIDTakoRight:
                    StretchSenseAPI.ble_updateTakoWithNotifications(self, data, cHandle, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUIDTakoBack:
                    StretchSenseAPI.ble_updateTakoWithNotifications(self, data, cHandle, self.addr)

                if myPeripheral.uuid == StretchSenseAPI.serviceUUIDTakoFront:
                    StretchSenseAPI.ble_updateTakoWithNotifications(self, data, cHandle, self.addr)
                break

"""

Global lists of values

"""

globalSensor = [StretchSensePeripheral()]


"""    Main initialisation

Main initial declaration to compile examples and files that you are using.

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
