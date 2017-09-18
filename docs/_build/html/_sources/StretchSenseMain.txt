2. StretchSense GUI Main
==========================

.. note:: Description of each functions and classes of the Raspberry Pi GUI.

.. automodule:: StretchSenseMain

------------------------------------ 

- .. py:class:: StretchSenseApp

	- .. automethod:: spiThreadDone(self)
	- .. automethod:: bleThreadDone(self)
	- .. automethod:: closeEvent(self)
	- .. automethod:: spiSettings(self)
	- .. automethod:: spiGetSettings(self)
	- .. automethod:: spiSetSettings(self)
	- .. automethod:: spiValueTable(self)
	- .. automethod:: spiRecordButton(self)
	- .. automethod:: spiRecordData(self)
	- .. automethod:: spiStopRecordData(self, data)
	- .. automethod:: bleScan(self)
	- .. automethod:: bleConnectInList(self)
	- .. automethod:: bleDisconnectInList(self)
	- .. automethod:: bleValueTable(self)
	- .. automethod:: bleRecordButton(self)
	- .. automethod:: bleRecordData(self)
	- .. automethod:: bleStopRecordData(self, data)
	- .. automethod:: mainTab(self)
	- .. automethod:: spiTab(self)
	- .. automethod:: spiSettingsTab(self)
	- .. automethod:: bleTab(self)
	- .. automethod:: bleValueTableTab(self)
	- .. automethod:: bleScanTab(self)
	- .. automethod:: bleBarGraphTab(self)
	- .. automethod:: bleLineGraphTab(self)
	- .. automethod:: infomationTab(self)
	- .. automethod:: disconnectButton(self)
	- .. automethod:: setValueBackgroundColor(self)
	- .. automethod:: recordData(self, recorded, filename)