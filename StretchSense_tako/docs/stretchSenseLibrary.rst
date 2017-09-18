1. StretchSense Library
==========================

.. note:: Description of each functions and classes of the Raspberry Pi API.

.. automodule:: stretchSenseLibrary

------------------------------------ 

- .. autoclass:: StretchSensePeripheral

------------------------------------------------ 

- .. py:class:: StretchSenseAPI

	- .. automethod:: spi_generateTenChannel(self)
	- .. automethod:: spi_setup(self)
	- .. automethod:: spi_mode(self)
	- .. automethod:: spi_triggerModeCapacitance(self)
	- .. automethod:: spi_continuousModeCapacitance(self)
	- .. automethod:: spi_writeConfiguration(self)
	- .. automethod:: spi_readCapacitance(self)
	- .. automethod:: spi_getCapacitanceScalingFactor(self, resolutionConfig)
	- .. automethod:: spi_extractCapacitance(self, raw, channel)
	- .. automethod:: spi_listToCsv(self)
	- .. automethod:: spi_getValuesCsv(self)
	- .. automethod:: spi_getListPeripheral(self)
	- .. automethod:: spi_close(self)
	- .. automethod:: ble_printAllPeripheralsAvailable(self)
	- .. automethod:: ble_printAllPeripheralsConnected(self)
	- .. automethod:: ble_scanning(self, scanTime)
	- .. automethod:: ble_connectOnePeripheral(self, myDeviceAddr)
	- .. automethod:: ble_connectAllPeripheral(self)
	- .. automethod:: ble_disconnectOnePeripheral(self, myDeviceAddr)
	- .. automethod:: ble_disconnectAllPeripherals(self)
	- .. automethod:: ble_updateAllPeripherals(self)
	- .. automethod:: ble_generateOneChannel(self, peripheral)
	- .. automethod:: ble_generateTenChannel(self, peripheral)
	- .. automethod:: ble_discoverServices(self)
	- .. automethod:: ble_discoverCharacteristics(self)
	- .. automethod:: ble_updateOneChannelWithNotifications(self, data, addr)
	- .. automethod:: ble_updateOneChannel(self)
	- .. automethod:: ble_updateTenChannelWithNotifications(self, data, addr)
	- .. automethod:: ble_updateTenChannel(self)
	- .. automethod:: ble_waitNotifications(self)
	- .. automethod:: ble_getListPeripheralAvailable(self)
	- .. automethod:: ble_getListAddrPeripheralAvailable(self)
	- .. automethod:: ble_getListPeripheralIsConnected(self)
	- .. automethod:: ble_getListPeripheralOnceConnected(self)
	- .. automethod:: ble_getListPeripheralInUse(self)
	- .. automethod:: ble_listToCsv(self)
	- .. automethod:: ble_getValuesCsv(self)