#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""

    - Website : https://www.stretchsense.com

    - Important : This StretchSense Library has been designed to enable the connection of one or more "StretchSense Sensor" and "StretchSense IC Boards" to your Raspberry Pi

    - Author : Louis Germain

    - Copyright : 2017 StretchSense

    - Date : 26/07/2017

    - Version : 1.0.0

"""

import stretchSenseLibrary
import sys
import time
from PyQt4 import QtGui, QtCore, uic


#stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()
#qtCreatorFile = 'StretchSense.ui'
#Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.mdi = QtGui.QMdiArea()
        self.centralWidget()


class StretchSenseApp(QtGui.QMainWindow): #, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.indexMain = 0
        self.indexSpi = 1
        self.indexSpiSettings = 2
        self.indexBluetooth = 3
        self.indexScan = 4
        self.indexBarGraph = 5
        self.indexLineGraph = 6
        self.indexValueTable = 7
        self.indexInformationTable = 8
        self.indexBluetoothShorted = 9
        self.rtSpi = 0
        self.rtBle = 0
        self.spiRecordingButton = True
        self.bleRecordingButton = True
        self.spiDataRecorded = ""
        self.dataRecorded = ""

        self.w_disconnectAll.clicked.connect(self.disconnectButton)
        self.w_disconnectAll2.clicked.connect(self.disconnectButton)
        self.w_disconnectAll3.clicked.connect(self.disconnectButton)
        self.w_disconnectAll4.clicked.connect(self.disconnectButton)
        self.w_disconnectAll5.clicked.connect(self.disconnectButton)
        self.w_disconnectAll6.clicked.connect(self.disconnectButton)
        self.w_backArrow.clicked.connect(self.bluetoothTab)
        self.w_backArrow1.clicked.connect(self.bluetoothTab)
        self.w_backArrow2.clicked.connect(self.bluetoothTab)
        self.w_backArrow3.clicked.connect(self.bluetoothTab)
        self.w_backArrow4.clicked.connect(self.mainTab)
        self.w_backArrow5.clicked.connect(self.mainTab)
        self.w_backArrow6.clicked.connect(self.mainTab)
        self.w_backArrow7.clicked.connect(self.spiTab)
        self.w_backArrow8.clicked.connect(self.mainTab)

        self.w_spiSelectButton.clicked.connect(self.spiTab)
        self.w_spiSettingsButton.clicked.connect(self.spiSettingsTab)
        self.w_bluetoothSelectButton.clicked.connect(self.bluetoothTab)
        self.w_scanningButton2.clicked.connect(self.scanTab)
        self.w_rescanButton.clicked.connect(self.scan)
        self.w_barGraphButton.clicked.connect(self.barGraphTab)
        self.w_lineGraphButton.clicked.connect(self.lineGraphTab)
        self.w_valueTableButton2.clicked.connect(self.valueTableTab)
        self.w_informationTabButton.clicked.connect(self.infomationTab)
        self.w_spiRecordButton.clicked.connect(self.spiRecordButton)
        self.w_bleRecordButton.clicked.connect(self.bleRecordButton)

        self.w_odrList.itemClicked.connect(self.spiSettings)
        self.w_interruptList.itemClicked.connect(self.spiSettings)
        self.w_triggerList.itemClicked.connect(self.spiSettings)
        self.w_filterList.itemClicked.connect(self.spiSettings)
        self.w_resolutionList.itemClicked.connect(self.spiSettings)
        self.w_listPeripheralPrinted.itemClicked.connect(self.connectInList)

        self.w_odrList.addItem("RATE OFF")
        self.w_odrList.addItem("RATE 25HZ")
        self.w_odrList.addItem("RATE 50HZ")
        self.w_odrList.addItem("RATE 100HZ")
        self.w_odrList.addItem("RATE 166HZ")
        self.w_odrList.addItem("RATE 200HZ")
        self.w_odrList.addItem("RATE 250HZ")
        self.w_odrList.addItem("RATE 500HZ")
        self.w_odrList.addItem("RATE 1KHZ")

        self.w_interruptList.addItem("INTERRUPT DISABLED")
        self.w_interruptList.addItem("INTERRUPT ENABLED")

        self.w_triggerList.addItem("TRIGGER DISABLED")
        self.w_triggerList.addItem("TRIGGER ENABLED")

        self.w_filterList.addItem("FILTER 0PT")
        self.w_filterList.addItem("FILTER 1PT")
        self.w_filterList.addItem("FILTER 3PT")
        self.w_filterList.addItem("FILTER 7PT")
        self.w_filterList.addItem("FILTER 15PT")
        self.w_filterList.addItem("FILTER 31PT")
        self.w_filterList.addItem("FILTER 63PT")
        self.w_filterList.addItem("FILTER 127PT")
        self.w_filterList.addItem("FILTER 255PT")

        self.w_resolutionList.addItem("RESOLUTION 1pF")
        self.w_resolutionList.addItem("RESOLUTION 100fF")
        self.w_resolutionList.addItem("RESOLUTION 10fF")
        self.w_resolutionList.addItem("RESOLUTION 1fF")

    def closeEvent(self, event):
        #print("closeEvent()")

        if self.rtSpi != 0:
            self.rtSpi.stop()
        if self.rtBle != 0:
            self.rtBle.stop()

        super(QtGui.QMainWindow, self).closeEvent(event)

    def spiSettings(self):
        #print("spiSettings()")

        """

        This function initialize the SPI settings list into the GUI .

        """
        if (self.w_odrList.currentItem() is None):
            pass
        elif (self.w_odrList.currentItem().text()[:3] == "RAT"):
            stretchSenseLibrary.ODR_MODE = self.w_odrList.currentRow()
            #print(stretchSenseLibrary.ODR_MODE)

        if (self.w_interruptList.currentItem() is None):
            pass
        elif (self.w_interruptList.currentItem().text()[:3] == "INT"):
            stretchSenseLibrary.INTERRUPT_MODE = self.w_interruptList.currentRow()
            #print(stretchSenseLibrary.INTERRUPT_MODE)

        if (self.w_triggerList.currentItem() is None):
            pass
        elif (self.w_triggerList.currentItem().text()[:3] == "TRI"):
            stretchSenseLibrary.TRIGGER_MODE = self.w_triggerList.currentRow()
            #print(stretchSenseLibrary.TRIGGER_MODE)

        if (self.w_filterList.currentItem() is None):
            pass
        elif (self.w_filterList.currentItem().text()[:3] == "FIL"):
            stretchSenseLibrary.FILTER_MODE = 2 ** (self.w_filterList.currentRow()) - 1
            #print(stretchSenseLibrary.FILTER_MODE)

        if (self.w_resolutionList.currentItem() is None):
            pass
        elif (self.w_resolutionList.currentItem().text()[:3] == "RES"):
            stretchSenseLibrary.RESOLUTION_MODE = self.w_resolutionList.currentRow()
            #print(stretchSenseLibrary.RESOLUTION_MODE)

        stretchsenseObject.spiSetup()

    def spiGetSettings(self):
        #print("spiGetSettings()")

        """
        Get settings on which are selected in the lists by the user.

        """
        for row in range(self.w_odrList.count()):
            if stretchSenseLibrary.ODR_MODE == row:
                myItem = self.w_odrList.item(row)
                myItem.setSelected(1)

        for row in range(self.w_interruptList.count()):
            if stretchSenseLibrary.INTERRUPT_MODE == row:
                myItem = self.w_interruptList.item(row)
                myItem.setSelected(1)

        for row in range(self.w_triggerList.count()):
            if stretchSenseLibrary.TRIGGER_MODE == row:
                myItem = self.w_triggerList.item(row)
                myItem.setSelected(1)

        for row in range(self.w_filterList.count()):
            if hex(stretchSenseLibrary.FILTER_MODE) == hex(2 ** row - 1):
                myItem = self.w_filterList.item(row)
                myItem.setSelected(1)

        for row in range(self.w_resolutionList.count()):
            if stretchSenseLibrary.RESOLUTION_MODE == row:
                myItem = self.w_resolutionList.item(row)
                myItem.setSelected(1)

    def spiSetSettings(self):
        #print("spiSetSettings()")

        """
        Submit the SPI settings chosen by the user onto the SPI bus via the API.

        """
        self.spiGetSettings()
        self.spiSettings()
        stretchsenseObject.spiSetup()

    def spiValueTable(self):
        #print("spiValueTable()")

        """

        Gets and displays SPI values in the GUI.

        """
        def spiUpdateValues(self):
            #print("spiUpdateValues()")

            stretchsenseObject.spiMode()
            if numberOfSpiPeripheral > 0:
                self.w_listSpiDataPrinted.clear()
                for myPeripheral in listPeripheralSpi:
                    self.w_listSpiDataPrinted.addItem(str("     SPI0 - Channel Number = " + str(myPeripheral.channelNumber) + "                  Value = " + str(myPeripheral.value) + " pF"))
            self.w_listSpiDataPrinted.update()
            self.t1 = time.time()
            self.t1 -= self.t0
            self.t1 = str(self.t1) + " ,"
            self.spiDataRecorded += str(self.counter) + " ," + str(self.t1)
            self.spiDataRecorded += stretchsenseObject.getValuesCsvSpi() + "\n"
            self.counter += 1
            time.sleep(0.05)

        self.spiSetSettings()
        stretchsenseObject.spiMode()
        listPeripheralSpi = stretchsenseObject.getListPeripheralSpi()
        numberOfSpiPeripheral = len(listPeripheralSpi)
        self.counter = 0
        self.spiDataRecorded = ""
        self.t0 = time.time()
        if numberOfSpiPeripheral > 0:
            self.rtSpi = stretchSenseLibrary.RepeatedTimer(0.1, lambda: spiUpdateValues(self))

    def spiRecordButton(self):
        #print("recordButton()")

        """

        Check if the SPI record button has been pushed.

        """

        if self.spiRecordingButton is True:
            self.spiRecordData()
        elif self.spiRecordingButton is False:
            self.spiStopRecordData(self.spiDataRecorded)

    def spiRecordData(self):
        #print("spiRecordData()")

        """

        If the SPI record button pushed, we start recording the data.

        """

        self.w_spiRecordButton.setText("Stop and save")
        self.spiDataRecorded = ""
        self.counter = 0
        self.t0 = time.time()
        self.spiRecordingButton = False

    def spiStopRecordData(self, data):
        #print("spiStopRecordData()")

        """

        Stop recording data and open the window to save the generated file.

        :param data: string :
            SPI Recorded data.

        """

        if self.spiRecordingButton is False:
            self.w_spiRecordButton.setText("Start recording")
            filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", "/home/pi", ".csv")
            if filename != 0:
                self.recordData(data, filename)
                self.spiRecordingButton = True
            else:
                self.w_generalTab.setCurrentIndex(self.mainTab)

    def scan(self):
        #print("scan()")

        """

        Start BLE scan by pushing the button.

        """

        self.w_rescanButton.setText("Rescan 3 seconds")
        self.w_listPeripheralPrinted.clear()
        self.scanTime = 3
        stretchsenseObject.scanning(self.scanTime)

        listPeripheralAvailable = stretchsenseObject.getListPeripheralAvailable()
        numberOfPeripheralAvailable = len(listPeripheralAvailable) - 1

        if numberOfPeripheralAvailable > 0:

            for myPeripheralAvailable in listPeripheralAvailable:

                if myPeripheralAvailable.addr != "":

                    self.w_listPeripheralPrinted.addItem(myPeripheralAvailable.addr)

    def connectInList(self):
        #print("connectInList()")

        """

        Connect the device the user chose via the API.

        """

        numberOfPeripheralPrinted = len(self.w_listPeripheralPrinted)

        if numberOfPeripheralPrinted > 0:
            if self.w_listPeripheralPrinted.isItemSelected(self.w_listPeripheralPrinted.currentItem()) is True:
                addr = self.w_listPeripheralPrinted.currentItem().text()
                stretchsenseObject.connectOnePeripheral(addr)
            else:
                self.disconnectInList()

    def disconnectInList(self):
        #print("disconnectInList()")

        """
        Disconnect the device selected by the user.

        """

        numberOfPeripheralPrinted = len(self.w_listPeripheralPrinted)

        if numberOfPeripheralPrinted > 0:
            addr = self.w_listPeripheralPrinted.currentItem().text()
            stretchsenseObject.disconnectOnePeripheral(addr)

    def valueTable(self):
        #print("valueTable()")

        """
        Gets and displays BLE values in the GUI.

        """

        def updateValues(self):
            #print("update()")

            #listPeripheralConnected = stretchsenseObject.getListPeripheralIsConnected()
            #numberOfPeripheralConnected = len(listPeripheralConnected)
            #print(numberOfPeripheralConnected)
            stretchsenseObject.waitNotifications()
            if numberOfPeripheralConnected > 0:
                if self.loop == 20:
                    self.w_listDataPrinted.clear()
                    for myPeripheral in listPeripheralConnected:
                        self.w_listDataPrinted.addItem(str("    Address = " + str(myPeripheral.addr) + "        Channel = " + str(myPeripheral.channelNumber) + "        Value = " + str(myPeripheral.value) + " pF"))
                        self.loop = 0
                    self.w_listDataPrinted.update()
            #else:
                #self.w_listSpiDataPrinted.clear()
                #self.rtBle.stop()
            self.t1 = time.time()
            self.t1 -= self.t0
            self.t1 = str(self.t1) + " ,"
            self.dataRecorded += str(self.counter) + " ," + str(self.t1)
            self.dataRecorded += stretchsenseObject.getValuesCsv() + "\n"
            self.counter += 1
            self.loop += 1
            time.sleep(0.005)

        listPeripheralConnected = stretchsenseObject.getListPeripheralIsConnected()
        numberOfPeripheralConnected = len(listPeripheralConnected)
        if listPeripheralConnected[0].addr != "":
            self.counter = 0
            self.dataRecorded = ""
            self.t0 = time.time()
            self.loop = 0

            self.rtBle = stretchSenseLibrary.RepeatedTimer(0.01, lambda: updateValues(self))

    def bleRecordButton(self):
        #print("bleRecordButton()")

        """
        Check if the BLE record button has been pushed.

        """

        if self.bleRecordingButton is True:
            self.bleRecordData()
        elif self.bleRecordingButton is False:
            self.bleStopRecordData(self.dataRecorded)

    def bleRecordData(self):
        #print("bleRecordData()")

        """
        If the BLE record button pushed, we start recording the data.

        """

        self.w_bleRecordButton.setText("Stop and save")
        self.dataRecorded = ""
        self.counter = 0
        self.t0 = time.time()
        self.bleRecordingButton = False

    def bleStopRecordData(self, data):
        #print("bleStopRecordData()")

        """
        Stop recording data and open the window to save the generated file.

        :param data: string :
            BLE Recorded data.

        """

        if self.bleRecordingButton is False:
            self.w_bleRecordButton.setText("Start recording")
            filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", "/home/pi", ".csv")
            if filename != 0:
                self.recordData(data, filename)
                self.bleRecordingButton = True
            else:
                self.w_generalTab.setCurrentIndex(self.indexBluetooth)

    def mainTab(self):
        #print("mainTab()")

        """
        Switch to main tab.

        """

        if self.spiDataRecorded == "":
            pass
        else:
            self.spiStopRecordData(self.spiDataRecorded)
            stretchsenseObject.closeSpi()

        if self.rtSpi != 0:
            self.rtSpi.stop()
        if self.rtBle != 0:
            self.rtBle.stop()
        else:
            pass

        self.w_generalTab.setCurrentIndex(self.indexMain)

    def spiTab(self):
        #print("spiTab()")

        """
        Switch to SPI tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexSpi)
        self.spiValueTable()

    def spiSettingsTab(self):
        #print("spiSettingsTab()")

        """
        Switch to SPI settings tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexSpiSettings)

    def bluetoothTab(self):
        #print("bluetoothTab()")

        """
        Switch to BLE tab.

        """

        if self.dataRecorded == "":
            pass
        else:
            self.bleStopRecordData(self.dataRecorded)

        if self.rtSpi != 0:
            self.rtSpi.stop()
        if self.rtBle != 0:
            self.rtBle.stop()
        else:
            pass
        self.w_generalTab.setCurrentIndex(self.indexBluetoothShorted)

    def valueTableTab(self):
        #print("valueTableTab()")

        """
        Switch to BLE value table tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexValueTable)
        self.valueTable()

    def scanTab(self):
        #print("scanTab()")

        """
        Switch to BLE scan tab.

        """

        self.disconnectButton()
        self.w_generalTab.setCurrentIndex(self.indexScan)
        self.w_rescanButton.setText("Scan 3 seconds")

    def barGraphTab(self):
        #print("barGraphTab()")

        """
        Switch to BLE barGraph tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexBarGraph)

    def lineGraphTab(self):
        #print("lineGraphTab()")

        """
        Switch to BLE lineGraph tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexLineGraph)

    def infomationTab(self):
        #print("informationTab()")

        """
        Switch to information tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexInformationTable)

    def disconnectButton(self):
        #print("disconnectButton()")

        """
        Disconnect every BLE peripherals by pushing the button.

        """

        if self.rtSpi != 0:
            self.rtSpi.stop()
        if self.rtBle != 0:
            self.rtBle.stop()

        stretchsenseObject.disconnectAllPeripheral()
        self.w_listPeripheralPrinted.clear()
        self.w_listDataPrinted.clear()

    def recordData(self, recorded, filename):
        #print("\033[0;35;40m recordData()\033[0m")

        """
        Open a new file and write the data in.

        :param recorded: string
            .csv file we want to record.

        :param filename: path
            Path to where we save the .csv file.

        """

        if filename != '':
            myFile = open(filename, "w+")
            myFile.write(recorded)
            myFile.close()


def main():
    print("Main()")

    app = QtGui.QApplication(sys.argv)
    window = StretchSenseApp()
    window.setWindowTitle("StretchSense")
    window.setWindowIcon(QtGui.QIcon("_Icons/StretchSense_Logo_Blue_resized_64x64.png"))
    window.show()
    sys.exit(app.exec_())
    StretchSenseApp.rtSpi.stop()
    StretchSenseApp.rtBle.stop()
    app.quit()

if __name__ == '__main__':

    main()
