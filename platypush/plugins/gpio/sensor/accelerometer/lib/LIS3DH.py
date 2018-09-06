#!/usr/bin/env python
"""
LIS3DH Python Library for Raspberry Pi
Created by Matt Dyson (mattdyson.org)
Project hosted at https://github.com/mattdy/python-lis3dh
Version 1.0 - 10/01/16
Version 1.1 - 19/03/16 (Mal Smalley) Adding click detection
Version 1.2 - 21/01/18 (holzfigure) Using new Adafruit library Adafruit_GPIO;
                                    Changing default busnumber (-1 -> 1);
                                    Fixing indentation issues;
                                    Increasing PEP8 and Python3 compatibility;
                                    Replacing variable name "range"
                                      (which is a keyword) with "g-range";

Requires the Adafruit_Python_GPIO library
https://github.com/adafruit/Adafruit_Python_GPIO

Inspiration and assistance from:
 - https://github.com/adafruit/Adafruit_LIS3DH
 - https://www.adafruit.com/datasheets/LIS3DH.pdf
"""

from Adafruit_GPIO import I2C
import RPi.GPIO as GPIO  # needed for Hardware interrupt


class LIS3DH:

    # I2C
    i2c = None
    I2C_ADDRESS_1 = 0x18
    I2C_ADDRESS_2 = 0x19
    # default
    I2C_DEFAULT = I2C_ADDRESS_1

    # bus
    BUS_NUMBER = 1  # -1

    # Ranges
    RANGE_2G  = 0b00  # default
    RANGE_4G  = 0b01
    RANGE_8G  = 0b10
    RANGE_16G = 0b11
    # default
    RANGE_DEFAULT = RANGE_2G

    # Refresh rates
    DATARATE_400HZ          = 0b0111  # 400Hz  # default
    DATARATE_200HZ          = 0b0110  # 200Hz
    DATARATE_100HZ          = 0b0101  # 100Hz
    DATARATE_50HZ           = 0b0100  # 50Hz
    DATARATE_25HZ           = 0b0011  # 25Hz
    DATARATE_10HZ           = 0b0010  # 10Hz
    DATARATE_1HZ            = 0b0001  # 1Hz
    DATARATE_POWERDOWN      = 0       # Power down
    DATARATE_LOWPOWER_1K6HZ = 0b1000  # Low power mode (1.6KHz)
    DATARATE_LOWPOWER_5KHZ  = 0b1001  # Low power mode (5KHz) / Normal power mode (1.25KHz)
    # default
    DATARATE_DEFAULT = DATARATE_400HZ

    # Registers
    REG_STATUS1       = 0x07
    REG_OUTADC1_L     = 0x08
    REG_OUTADC1_H     = 0x09
    REG_OUTADC2_L     = 0x0A
    REG_OUTADC2_H     = 0x0B
    REG_OUTADC3_L     = 0x0C
    REG_OUTADC3_H     = 0x0D
    REG_INTCOUNT      = 0x0E
    REG_WHOAMI        = 0x0F  # Device identification register
    REG_TEMPCFG       = 0x1F
    REG_CTRL1         = 0x20  # Used for data rate selection, and enabling/disabling individual axis
    REG_CTRL2         = 0x21
    REG_CTRL3         = 0x22
    REG_CTRL4         = 0x23  # Used for BDU, scale selection, resolution selection and self-testing
    REG_CTRL5         = 0x24
    REG_CTRL6         = 0x25
    REG_REFERENCE     = 0x26
    REG_STATUS2       = 0x27
    REG_OUT_X_L       = 0x28
    REG_OUT_X_H       = 0x29
    REG_OUT_Y_L       = 0x2A
    REG_OUT_Y_H       = 0x2B
    REG_OUT_Z_L       = 0x2C
    REG_OUT_Z_H       = 0x2D
    REG_FIFOCTRL      = 0x2E
    REG_FIFOSRC       = 0x2F
    REG_INT1CFG       = 0x30
    REG_INT1SRC       = 0x31
    REG_INT1THS       = 0x32
    REG_INT1DUR       = 0x33
    REG_CLICKCFG      = 0x38
    REG_CLICKSRC      = 0x39
    REG_CLICKTHS      = 0x3A
    REG_TIMELIMIT     = 0x3B
    REG_TIMELATENCY   = 0x3C
    REG_TIMEWINDOW    = 0x3D

    # Values
    DEVICE_ID  = 0x33
    INT_IO     = 0x04  # GPIO pin for interrupt
    CLK_NONE   = 0x00
    CLK_SINGLE = 0x01
    CLK_DOUBLE = 0x02

    AXIS_X = 0x00
    AXIS_Y = 0x01
    AXIS_Z = 0x02

    # changed busnumber to 1 (from -1)
    # alternative i2c address=0x19
    def __init__(self, address=I2C_DEFAULT, bus=BUS_NUMBER,
                 g_range=RANGE_DEFAULT, datarate=DATARATE_DEFAULT,
                 debug=False):
        self.isDebug = debug
        self.debug("Initialising LIS3DH")

        # self.i2c = Adafruit_I2C(address, busnum=bus)
        self.i2c = I2C.Device(address, busnum=bus)
        self.address = address

        try:
            val = self.i2c.readU8(self.REG_WHOAMI)
            if val != self.DEVICE_ID:
                # raise Exception(("Device ID incorrect - expected 0x%X, " +
                #                  "got 0x%X at address 0x%X") % (
                #                          self.DEVICE_ID, val, self.address))
                raise Exception(("Device ID incorrect - expected 0x{:x}, " +
                                 "got 0x{:x} at address 0x{:x}").format(
                                     self.DEVICE_ID, val, self.address))

            self.debug(("Successfully connected to LIS3DH " +
                        "at address 0x{:x}").format(self.address))
        except Exception as e:
            print("Error establishing connection with LIS3DH")
            print(e)

        # Enable all axis
        self.setAxisStatus(self.AXIS_X, True)
        self.setAxisStatus(self.AXIS_Y, True)
        self.setAxisStatus(self.AXIS_Z, True)

        # Set refresh rate (default: 400Hz)
        self.setDataRate(datarate)

        self.setHighResolution()
        self.setBDU()

        self.setRange(g_range)

    # Get reading from X axis
    def getX(self):
        return self.getAxis(self.AXIS_X)

    # Get reading from Y axis
    def getY(self):
        return self.getAxis(self.AXIS_Y)

    # Get reading from Z axis
    def getZ(self):
        return self.getAxis(self.AXIS_Z)

    # Get a reading from the desired axis
    def getAxis(self, axis):
        # Determine which register we need to read from (2 per axis)
        base = self.REG_OUT_X_L + (2 * axis)

        # Read the first register (lower bits)
        low = self.i2c.readU8(base)
        # Read the next register (higher bits)
        high = self.i2c.readU8(base + 1)
        # Combine the two components
        res = low | (high << 8)
        # Calculate the twos compliment of the result
        res = self.twosComp(res)

        # Fetch the range we're set to, so we can
        # accurately calculate the result
        g_range = self.getRange()
        divisor = 1
        if g_range == self.RANGE_2G:    divisor = 16380
        elif g_range == self.RANGE_4G:  divisor = 8190
        elif g_range == self.RANGE_8G:  divisor = 4096
        elif g_range == self.RANGE_16G: divisor = 1365.33

        return float(res) / divisor

    # Get the range that the sensor is currently set to
    def getRange(self):
        val = self.i2c.readU8(self.REG_CTRL4)  # Get value from register
        val = (val >> 4)  # Remove lowest 4 bits
        val &= 0b0011  # Mask off two highest bits

        if val == self.RANGE_2G:   return self.RANGE_2G
        elif val == self.RANGE_4G: return self.RANGE_4G
        elif val == self.RANGE_8G: return self.RANGE_8G
        else:                      return self.RANGE_16G

    # Set the range of the sensor (2G, 4G, 8G, 16G)
    def setRange(self, g_range):
        if g_range < 0 or g_range > 3:
            raise Exception("Tried to set invalid range")

        val = self.i2c.readU8(self.REG_CTRL4)  # Get value from register
        val &= ~(0b110000)  # Mask off lowest 4 bits
        val |= (g_range << 4)  # Write in our new range
        self.writeRegister(self.REG_CTRL4, val)  # Write back to register

    # Enable or disable an individual axis
    # Read status from CTRL_REG1, then write back with
    # appropriate status bit changed
    def setAxisStatus(self, axis, enable):
        if axis < 0 or axis > 2:
            raise Exception("Tried to modify invalid axis")

        current = self.i2c.readU8(self.REG_CTRL1)
        status = 1 if enable else 0
        final = self.setBit(current, axis, status)
        self.writeRegister(self.REG_CTRL1, final)

    def setInterrupt(self, mycallback):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INT_IO, GPIO.IN)
        GPIO.add_event_detect(self.INT_IO, GPIO.RISING, callback=mycallback)

    def setClick(self, clickmode, clickthresh=80,
                 timelimit=10, timelatency=20, timewindow=100,
                 mycallback=None):
        if (clickmode == self.CLK_NONE):
            val = self.i2c.readU8(self.REG_CTRL3)  # Get value from register
            val &= ~(0x80)  # unset bit 8 to disable interrupt
            self.writeRegister(self.REG_CTRL3, val)  # Write back to register
            self.writeRegister(self.REG_CLICKCFG, 0)  # disable all interrupts
            return
        self.writeRegister(self.REG_CTRL3, 0x80)  # turn on int1 click
        self.writeRegister(self.REG_CTRL5, 0x08)  # latch interrupt on int1

        if (clickmode == self.CLK_SINGLE):
            # turn on all axes & singletap
            self.writeRegister(self.REG_CLICKCFG, 0x15)
        if (clickmode == self.CLK_DOUBLE):
            # turn on all axes & doubletap
            self.writeRegister(self.REG_CLICKCFG, 0x2A)

        # set timing parameters
        self.writeRegister(self.REG_CLICKTHS, clickthresh)
        self.writeRegister(self.REG_TIMELIMIT, timelimit)
        self.writeRegister(self.REG_TIMELATENCY, timelatency)
        self.writeRegister(self.REG_TIMEWINDOW, timewindow)

        if mycallback is not None:
            self.setInterrupt(mycallback)

    def getClick(self):
        reg = self.i2c.readU8(self.REG_CLICKSRC)  # read click register
        self.i2c.readU8(self.REG_INT1SRC)         # reset interrupt flag
        return reg

    # Set the rate (cycles per second) at which data is gathered
    def setDataRate(self, dataRate):
        val = self.i2c.readU8(self.REG_CTRL1)  # Get current value
        val &= 0b1111  # Mask off lowest 4 bits
        val |= (dataRate << 4)  # Write in our new data rate to highest 4 bits
        self.writeRegister(self.REG_CTRL1, val)  # Write back to register

    # Set whether we want to use high resolution or not
    def setHighResolution(self, highRes=True):
        val = self.i2c.readU8(self.REG_CTRL4)  # Get current value
        status = 1 if highRes else 0

        # High resolution is bit 4 of REG_CTRL4
        final = self.setBit(val, 3, status)
        self.writeRegister(self.REG_CTRL4, final)

    # Set whether we want to use block data update or not
    # False = output registers not updated until MSB and LSB reading
    def setBDU(self, bdu=True):
        val = self.i2c.readU8(self.REG_CTRL4)  # Get current value
        status = 1 if bdu else 0

        # Block data update is bit 8 of REG_CTRL4
        final = self.setBit(val, 7, status)
        self.writeRegister(self.REG_CTRL4, final)

    # Write the given value to the given register
    def writeRegister(self, register, value):
        self.debug("WRT {} to register 0x{:x}".format(
            bin(value), register))
        self.i2c.write8(register, value)

    # Set the bit at index 'bit' to 'value' on 'input' and return
    def setBit(self, input, bit, value):
        mask = 1 << bit
        input &= ~mask
        if value:
            input |= mask
        return input

    # Return a 16-bit signed number (two's compliment)
    # Thanks to http://stackoverflow.com/questions/16124059/trying-to-
    #   read-a-twos-complement-16bit-into-a-signed-decimal
    def twosComp(self, x):
        if (0x8000 & x):
            x = - (0x010000 - x)
        return x

    # Print an output of all registers
    def dumpRegisters(self):
        for x in range(0x0, 0x3D):
            read = self.i2c.readU8(x)
            print("{:x}: {}".format(x, bin(read)))

    def debug(self, message):
        if not self.isDebug:
            return
        print(message)
