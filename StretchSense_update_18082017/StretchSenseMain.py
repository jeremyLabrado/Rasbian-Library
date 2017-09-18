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


stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()
qtCreatorFile = 'StretchSense.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.mdi = QtGui.QMdiArea()
        self.centralWidget()


class SpiThread(QtCore.QThread):

    def __init__(self):
        super(SpiThread, self).__init__()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.run)

    def start(self):
        self.timer.start()
        self.run()

    def stop(self):
        self.timer.stop()

    def run(self):
        stretchsenseObject.spi_mode()
        self.emit(QtCore.SIGNAL("spiThreadDone()"))


class BleThread(QtCore.QThread):

    def __init__(self):
        super(BleThread, self).__init__()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.run)

    def start(self):
        self.timer.start()
        self.run()

    def stop(self):
        self.timer.stop()

    def run(self):
        stretchsenseObject.ble_waitNotifications()
        self.emit(QtCore.SIGNAL("bleThreadDone()"))


class QCustomScanWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(QCustomScanWidget, self).__init__(parent)
        self.textQVBoxLayout = QtGui.QVBoxLayout()
        self.textUpQLabel = QtGui.QLabel()
        self.textDownQLabel = QtGui.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        #self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout = QtGui.QHBoxLayout()
        self.iconQLabel = QtGui.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        self.myListOfScanWidget = []

        # Set stylesheet

        self.textUpQLabel.setStyleSheet('''background-color: rgba(0, 0, 0, 0);
                                                font: 75 12pt "Roboto";
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent''')

        self.textDownQLabel.setStyleSheet('''background-color: rgba(0, 0, 0, 0);
                                                font: 75 10pt "Roboto";
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent''')

        self.iconQLabel.setStyleSheet('''       background-color: rgba(255, 255, 255, 0);
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent;''')

    def setTextUp(self, text):
        self.textUpQLabel.setText(text)

    def setTextDown(self, text):
        self.textDownQLabel.setText(text)

    def setIcon(self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))

    def myListOfScanWidget(self, myWidget):
        self.myListOfScanWidget.append(myWidget)

    def setWidget(self, addr):  #, gen):

        self.setTextUp(str(addr))
        #self.setTextDown(str(gen))
        self.setIcon("_Icons/StretchSense_Logo_Blue_resized_15x15.png")


class QCustomQWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QtGui.QVBoxLayout()
        self.textUpQLabel = QtGui.QLabel()
        self.textMiddleQLabel = QtGui.QLabel()
        self.textDownQLabel = QtGui.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textMiddleQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout = QtGui.QHBoxLayout()
        self.iconQLabel = QtGui.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        self.myListOfCustomWidget = []

        # Set stylesheet

        self.textUpQLabel.setStyleSheet('''background-color: rgba(0, 0, 0, 0);
                                                color: rgb(0, 174, 239);
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent;''')
        self.textMiddleQLabel.setStyleSheet('''background-color: rgba(0, 0, 0, 0);
                                                color: rgb(63, 199, 189);
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent;''')
        self.textDownQLabel.setStyleSheet('''background-color: rgba(0, 0, 0, 0);
                                                color: rgb(237, 61, 150);
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent;''')
        self.iconQLabel.setStyleSheet('''       background-color: rgba(255, 255, 255, 0);
                                                border-style: solid;
                                                border-width: 1px;
                                                border-color: transparent;''')

    def setTextUp(self, text):
        self.textUpQLabel.setText("Address = " + text)

    def setTextMiddle(self, text):
        self.textMiddleQLabel.setText("Channel Number = " + text)

    def setTextDowm(self, text):
        self.textDownQLabel.setText("Value = " + text + " pF")

    def setIcon(self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))

    def listOfCustomWidget(self, myWidget):

        self.myListOfCustomWidget.append(myWidget)

    def setWidget(self, addr, index, value):

        self.setTextUp(str(addr))
        self.setTextMiddle(str(index))
        self.setTextDowm(str(value))
        self.setIcon("_Icons/StretchSense_Logo_Blue_resized_15x15.png")

    def update(self, addr, index, value):

        self.setTextUp(str(addr))
        self.setTextMiddle(str(index + 1))
        self.setTextDowm(str(value))
        if (value >= 50 and value <= 600):
            self.iconQLabel.setStyleSheet('''background-color: rgb(0, 255, 0);
                                             border-color: transparent;''')
        else:
            self.iconQLabel.setStyleSheet('''background-color: rgba(255, 0, 0, 160);
                                             border-color: transparent;''')


class StretchSenseApp(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.indexMain = 0
        self.indexSpi = 1
        self.indexSpiSettings = 2
        self.indexBle = 3
        self.indexScan = 4
        self.indexBarGraph = 5
        self.indexLineGraph = 6
        self.indexValueTable = 7
        self.indexInformationTable = 8
        self.indexBleShorted = 9
        self.spiRecordingButton = True
        self.bleRecordingButton = True
        self.spiDataRecorded = ""
        self.dataRecorded = ""
        self.myCustomQWidget = QCustomQWidget()
        self.listOfCustomWidget = []
        self.myListOfScanWidget = []
        self.t0 = time.time()
        self.counter = 0
        self.myAddrToCheck = ""
        self.backgroundWhite = '''rgb(255, 255, 255)'''
        self.backgroundGrey = '''rgb(204, 204, 204)'''

        self.SpiThread = SpiThread()
        self.BleThread = BleThread()

        self.connect(self.SpiThread, QtCore.SIGNAL("spiThreadDone()"), self.spiThreadDone, QtCore.Qt.DirectConnection)
        self.connect(self.BleThread, QtCore.SIGNAL("bleThreadDone()"), self.bleThreadDone, QtCore.Qt.DirectConnection)

        self.w_disconnectAll.clicked.connect(self.disconnectButton)
        self.w_disconnectAll2.clicked.connect(self.disconnectButton)
        self.w_disconnectAll3.clicked.connect(self.disconnectButton)
        self.w_disconnectAll4.clicked.connect(self.disconnectButton)
        self.w_disconnectAll5.clicked.connect(self.disconnectButton)
        self.w_stopSpiCommunication.clicked.connect(self.disconnectButton)
        self.w_backArrow.clicked.connect(self.bleTab)
        self.w_backArrow1.clicked.connect(self.bleTab)
        self.w_backArrow2.clicked.connect(self.bleTab)
        self.w_backArrow3.clicked.connect(self.bleTab)
        self.w_backArrow4.clicked.connect(self.mainTab)
        self.w_backArrow5.clicked.connect(self.mainTab)
        self.w_backArrow6.clicked.connect(self.mainTab)
        self.w_backArrow7.clicked.connect(self.spiTab)
        self.w_backArrow8.clicked.connect(self.mainTab)

        self.w_spiSelectButton.clicked.connect(self.spiTab)
        self.w_spiSettingsButton.clicked.connect(self.spiSettingsTab)
        self.w_bleSelectButton.clicked.connect(self.bleTab)
        self.w_scanningButton2.clicked.connect(self.bleScanTab)
        self.w_rescanButton.clicked.connect(self.bleScan)
        self.w_barGraphButton.clicked.connect(self.bleBarGraphTab)
        self.w_lineGraphButton.clicked.connect(self.bleLineGraphTab)
        self.w_valueTableButton2.clicked.connect(self.bleValueTableTab)
        self.w_informationTabButton.clicked.connect(self.infomationTab)
        self.w_spiRecordButton.clicked.connect(self.spiRecordButton)
        self.w_bleRecordButton.clicked.connect(self.bleRecordButton)

        self.w_odrList.itemClicked.connect(self.spiSettings)
        self.w_interruptList.itemClicked.connect(self.spiSettings)
        self.w_triggerList.itemClicked.connect(self.spiSettings)
        self.w_filterList.itemClicked.connect(self.spiSettings)
        self.w_resolutionList.itemClicked.connect(self.spiSettings)
        self.w_listPeripheralPrinted.clicked.connect(self.bleConnectInList)

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

    def spiThreadDone(self):
        #print("spiThreadDone()")

        """
        Action triggerd by the BLE thread that updates our values

        """

        for i in range(len(self.listOfCustomWidget)):
            self.listOfCustomWidget[i].update(self.listPeripheralSpi[i].addr, self.listPeripheralSpi[i].channelNumber, self.listPeripheralSpi[i].value)

        self.t1 = time.time()
        self.t1 -= self.t0
        self.t1 = str(self.t1) + " ,"
        self.spiDataRecorded += str(self.counter) + " ," + str(self.t1)
        self.spiDataRecorded += stretchsenseObject.spi_getValuesCsv() + "\n"
        self.counter += 1

    def bleThreadDone(self):
        #print("bleThreadDone()")

        """
        Action triggerd by the BLE thread that updates our values

        """

        for i in range(len(self.listOfCustomWidget)):
            self.listOfCustomWidget[i].update(self.listPeripheralConnected[i].addr, self.listPeripheralConnected[i].channelNumber, self.listPeripheralConnected[i].value)

        self.t1 = time.time()
        self.t1 -= self.t0
        self.t1 = str(self.t1) + " ,"
        self.dataRecorded += str(self.counter) + " ," + str(self.t1)
        self.dataRecorded += stretchsenseObject.ble_getValuesCsv() + "\n"
        self.counter += 1

    def closeEvent(self, event):
        #print("closeEvent()")

        """
        Close the window and make sure that all thread are stopped

        """
        if self.SpiThread != 0:
            self.SpiThread.stop()
        if self.BleThread != 0:
            self.BleThread.stop()

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

        stretchsenseObject.spi_setup()

    def spiGetSettings(self):
        #print("spiGetSettings()")

        """

        Get settings which are selected by the user in the lists.

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
        stretchsenseObject.spi_setup()

    def spiValueTable(self):
        #print("spiValueTable()")

        """
        Gets and displays SPI values in the GUI.

        """

        self.spiSetSettings()
        stretchsenseObject.spi_mode()
        self.listPeripheralSpi = stretchsenseObject.spi_getListPeripheral()
        numberOfSpiPeripheral = len(self.listPeripheralSpi)
        self.listOfCustomWidget.clear()

        if numberOfSpiPeripheral > 0:

            self.SpiThread.start()
            self.w_listSpiDataPrinted.clear()

            for myPeripheral in self.listPeripheralSpi:

                self.myCustomQWidget = QCustomQWidget()

                addr = myPeripheral.addr
                index = int(myPeripheral.channelNumber)
                value = myPeripheral.value
                self.listOfCustomWidget.append(self.myCustomQWidget)
                self.myCustomQWidget.setWidget(addr, index, value)

                # Create QlistWidgetItem
                self.myQListWidgetItem = QtGui.QListWidgetItem(self.w_listSpiDataPrinted)

                # Set Size hint
                self.myQListWidgetItem.setSizeHint(self.myCustomQWidget.sizeHint())

                # Add QListWidgetItem into QListWidget
                self.w_listSpiDataPrinted.addItem(self.myQListWidgetItem)
                self.w_listSpiDataPrinted.setItemWidget(self.myQListWidgetItem, self.myCustomQWidget)

    def spiRecordButton(self):
        #print("spiRecordButton()")

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
        self.spiDataRecorded = "#, Sample Time         , SSL1, SSL2, SSL3, SSL4, SSL5, SSL6, SSL7, SSL8, SSL9, SSL10" + "\n"
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

    def bleScan(self):
        #print("bleScan()")

        """

        Start BLE scan by pushing the button.

        """
        self.w_listPeripheralPrinted.clear()
        self.w_rescanButton.setText("Rescan 3 seconds")
        self.scanTime = 3
        stretchsenseObject.ble_scanning(self.scanTime)
        self.myListOfScanWidget.clear()

        listPeripheralAvailable = stretchsenseObject.ble_getListPeripheralAvailable()
        numberOfPeripheralAvailable = len(listPeripheralAvailable) - 1

        if numberOfPeripheralAvailable > 0:

            for myPeripheralAvailable in listPeripheralAvailable:

                if myPeripheralAvailable.addr != "":
                    self.myCustomQWidget = QCustomScanWidget()

                    addr = myPeripheralAvailable.addr
                    #gen = myPeripheralAvailable.gen
                    self.myListOfScanWidget.append(self.myCustomQWidget)
                    self.myCustomQWidget.setWidget(addr)  #, gen)
                    #self.w_listPeripheralPrinted.addItem(myPeripheralAvailable.addr)

                    # Create QlistWidgetItem
                    self.myQListWidgetItem = QtGui.QListWidgetItem(self.w_listPeripheralPrinted)

                    # Set Size hint
                    self.myQListWidgetItem.setSizeHint(self.myCustomQWidget.sizeHint())

                    # Add QListWidgetItem into QListWidget
                    self.w_listPeripheralPrinted.addItem(self.myQListWidgetItem)
                    self.w_listPeripheralPrinted.setItemWidget(self.myQListWidgetItem, self.myCustomQWidget)

    def bleConnectInList(self):
        #print("bleConnectInList()")

        """

        Connect the device the user chose via the API.

        """

        numberOfPeripheralPrinted = len(self.w_listPeripheralPrinted)
        if numberOfPeripheralPrinted > 0:
            if self.w_listPeripheralPrinted.isItemSelected(self.w_listPeripheralPrinted.currentItem()) is True:
                row = self.w_listPeripheralPrinted.currentRow()
                addr = self.myListOfScanWidget[row].textUpQLabel.text()
                stretchsenseObject.ble_connectOnePeripheral(addr)
        else:
            self.disconnectInList()

    def bleDisconnectInList(self):
        #print("bleDisconnectInList()")

        """
        Disconnect the device selected by the user.

        """

        numberOfPeripheralPrinted = len(self.w_listPeripheralPrinted)

        if numberOfPeripheralPrinted > 0:
            addr = self.w_listPeripheralPrinted.currentItem().text()
            stretchsenseObject.ble_disconnectOnePeripheral(addr)

    def bleValueTable(self):
        print("bleValueTable()")

        """
        Gets and displays BLE values in the GUI.

        """

        stretchsenseObject.ble_waitNotifications()
        self.listPeripheralConnected = stretchsenseObject.ble_getListPeripheralIsConnected()
        numberOfPeripheralConnected = len(self.listPeripheralConnected)
        self.listOfCustomWidget.clear()

        if numberOfPeripheralConnected > 0:

            self.BleThread.start()
            self.w_listDataPrinted.clear()
            for myPeripheral in self.listPeripheralConnected:

                self.myCustomQWidget = QCustomQWidget()
                addr = myPeripheral.addr
                index = int(myPeripheral.channelNumber)
                value = myPeripheral.value
                self.listOfCustomWidget.append(self.myCustomQWidget)
                self.myCustomQWidget.setWidget(addr, index, value)

                if ((addr != self.myAddrToCheck) and (self.myAddrToCheck != "")):
                    mySize = QtCore.QSize()
                    mySize.setHeight(3)
                    barItem = QtGui.QListWidgetItem(self.w_listDataPrinted)
                    barItem.setBackgroundColor(QtGui.QColor(0, 174, 239))
                    barItem.setSizeHint(mySize)
                    self.w_listDataPrinted.addItem(barItem)

                self.myAddrToCheck = addr

                # Create QlistWidgetItem
                self.myQListWidgetItem = QtGui.QListWidgetItem(self.w_listDataPrinted)

                # Set Size hint
                self.myQListWidgetItem.setSizeHint(self.myCustomQWidget.sizeHint())

                # Add QListWidgetItem into QListWidget
                self.w_listDataPrinted.addItem(self.myQListWidgetItem)
                self.w_listDataPrinted.setItemWidget(self.myQListWidgetItem, self.myCustomQWidget)

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
        self.dataRecorded = "#, Sample Time         , Samples" + "\n"
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
                self.w_generalTab.setCurrentIndex(self.indexBle)

    def mainTab(self):
        #print("mainTab()")

        """
        Switch to main tab.

        """

        if self.spiDataRecorded == "":
            pass
        else:
            self.spiStopRecordData(self.spiDataRecorded)
            stretchsenseObject.spi_close()

        if self.SpiThread != 0:
            self.SpiThread.stop()
        if self.BleThread != 0:
            self.BleThread.stop()
        else:
            pass

        self.w_listPeripheralPrinted.clear()
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

    def bleTab(self):
        #print("bleTab()")

        """
        Switch to BLE tab.

        """

        if self.dataRecorded == "":
            pass
        else:
            self.bleStopRecordData(self.dataRecorded)

        if self.SpiThread != 0:
            self.SpiThread.stop()
        if self.BleThread != 0:
            self.BleThread.stop()
        else:
            pass
        self.w_generalTab.setCurrentIndex(self.indexBleShorted)

    def bleValueTableTab(self):
        #print("bleValueTableTab()")

        """
        Switch to BLE value table tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexValueTable)
        self.bleValueTable()

    def bleScanTab(self):
        #print("bleScanTab()")

        """
        Switch to BLE scan tab.

        """

        self.disconnectButton()
        self.w_generalTab.setCurrentIndex(self.indexScan)
        self.w_rescanButton.setText("Scan 3 seconds")

    def bleBarGraphTab(self):
        #print("bleBarGraphTab()")

        """
        Switch to BLE barGraph tab.

        """

        self.w_generalTab.setCurrentIndex(self.indexBarGraph)

    def bleLineGraphTab(self):
        #print("bleLineGraphTab()")

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

        if self.SpiThread != 0:
            self.SpiThread.stop()
        if self.BleThread != 0:
            self.BleThread.stop()

        stretchsenseObject.ble_disconnectAllPeripherals()
        self.listOfCustomWidget.clear()
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
    StretchSenseApp.SpiThread.stop()
    StretchSenseApp.BleThread.stop()
    app.quit()

if __name__ == '__main__':

    main()
