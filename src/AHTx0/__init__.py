# SPDX-FileCopyrightText: 2020 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""

`ahtx0`
=================================================================
Driver for the Adafruit AHT10/AHT20 Temperature & Humidity Sensor
* Author(s): Kattni Rembor
* Modified by: Steve Wadsworth

Implementation Notes
--------------------
**Hardware:**
* `Adafruit AHT20 Temperature & Humidity Sensor breakout:
  <https://www.adafruit.com/product/4566>`_ (Product ID: 4566)
**Software and Dependencies:**
* `MicroPython:
  <https://micropython.org>`

"""

import time
from micropython import const

AHTX0_I2CADDR_DEFAULT = const(0x38)  # Default I2C address
AHTX0_CMD_CALIBRATE = const(0xE1)  # Calibration command
AHTX0_CMD_TRIGGER = const(0xAC)  # Trigger reading command
AHTX0_CMD_SOFTRESET = const(0xBA)  # Soft reset command
AHTX0_STATUS_BUSY = const(0x80)  # Status bit for busy
AHTX0_STATUS_CALIBRATED = const(0x08)  # Status bit for calibrated


class AHTx0:
    """
    Interface library for AHT10/AHT20 temperature+humidity sensors.
    Taken from the Adafruit driver of the same name and modified to only
    depend on MicroPython, specifically machine.I2C

    :param machine.I2C i2c_bus: The I2C bus the AHT10/AHT20 is connected to.
    :param int address: The I2C device address. Default is :const:`0x38`

    **Quickstart: Importing and using the AHT10/AHT20 temperature sensor**
        Here is an example of using the :class:`AHTx0` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python
            import machine
            from AHTx0 import *

        Once this is done you can define your `machine.I2C` object and define your sensor object

        .. code-block:: python

            sda = machine.Pin(4)
            scl = machine.Pin(5)
            i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
            sensor = AHTx0(i2c)

        Now you have access to the temperature and humidity using
        the :attr:`temperature` and :attr:`relative_humidity` attributes

        .. code-block:: python

            temperature = sensor.temperature
            relative_humidity = sensor.relative_humidity

    """

    def __init__(self, i2c_bus, address=AHTX0_I2CADDR_DEFAULT):
        time.sleep(0.02)  # 20ms delay to wake up
        self.i2c_bus = i2c_bus
        self.address = address
        self.reset()
        if not self.calibrate():
            raise RuntimeError("Could not calibrate")
        self._temp = None
        self._humidity = None

    def reset(self):
        """Perform a soft-reset of the AHT"""
        buf = bytearray(1)
        buf[0] = AHTX0_CMD_SOFTRESET
        self.i2c_bus.writeto(self.address, buf)
        time.sleep(0.02)  # 20ms delay to wake up

    def calibrate(self):
        """Ask the sensor to self-calibrate. Returns True on success, False otherwise"""
        buf = bytearray(3)
        buf[0] = AHTX0_CMD_CALIBRATE
        buf[1] = 0x08
        buf[2] = 0x00
        self.i2c_bus.writeto(self.address, buf)
        while self.status & AHTX0_STATUS_BUSY:
            time.sleep(0.01)
        if not self.status & AHTX0_STATUS_CALIBRATED:
            return False
        return True

    @property
    def status(self):
        """The status byte initially returned from the sensor, see datasheet for details"""
        buf = self.i2c_bus.readfrom(self.address, 1)
        # print("status: "+hex(buf[0]))
        return buf[0]

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        self._readdata()
        return self._humidity

    @property
    def temperature(self):
        """The measured temperature in degrees Celsius."""
        self._readdata()
        return self._temp

    def _readdata(self):
        """Internal function for triggering the AHT to read temp/humidity"""
        buf = bytearray(3)
        buf[0] = AHTX0_CMD_TRIGGER
        buf[1] = 0x33
        buf[2] = 0x00
        self.i2c_bus.writeto(self.address, buf)
        while self.status & AHTX0_STATUS_BUSY:
            time.sleep(0.01)
        buf = self.i2c_bus.readfrom(self.address, 6)

        self._humidity = (
            (buf[1] << 12) | (buf[2] << 4) | (buf[3] >> 4)
        )
        self._humidity = (self._humidity * 100) / 0x100000
        self._temp = ((buf[3] & 0xF) << 16) | (buf[4] << 8) | buf[5]
        self._temp = ((self._temp * 200.0) / 0x100000) - 50
