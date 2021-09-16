#!/usr/bin/env python
# coding: latin-1
"""
This module is designed to communicate with the ZeroBorg

Use by creating an instance of the class, call the Init function, then command as desired, e.g.
import ZeroBorg
ZB = ZeroBorg.ZeroBorg()
ZB.Init()
# User code here, use ZB to control the board

Multiple boards can be used when configured with different I?C addresses by creating multiple instances, e.g.
import ZeroBorg
ZB1 = ZeroBorg.ZeroBorg()
ZB2 = ZeroBorg.ZeroBorg()
ZB1.i2cAddress = 0x44
ZB2.i2cAddress = 0x45
ZB1.Init()
ZB2.Init()
# User code here, use ZB1 and ZB2 to control each board separately

For explanations of the functions available call the Help function, e.g.
import ZeroBorg
ZB = ZeroBorg.ZeroBorg()
ZB.Help()
See the website at www.piborg.org/zeroborg for more details
"""

# Import the libraries we need
import io
import fcntl
import types
import time

# Constant values
I2C_SLAVE = 0x0703
PWM_MAX = 255
I2C_NORM_LEN = 4
I2C_LONG_LEN = 24

I2C_ID_ZEROBORG = 0x40

COMMAND_SET_LED = 1  # Set the LED status
COMMAND_GET_LED = 2  # Get the LED status
COMMAND_SET_A_FWD = 3  # Set motor 1 PWM rate in a forwards direction
COMMAND_SET_A_REV = 4  # Set motor 1 PWM rate in a reverse direction
COMMAND_GET_A = 5  # Get motor 1 direction and PWM rate
COMMAND_SET_B_FWD = 6  # Set motor 2 PWM rate in a forwards direction
COMMAND_SET_B_REV = 7  # Set motor 2 PWM rate in a reverse direction
COMMAND_GET_B = 8  # Get motor 2 direction and PWM rate
COMMAND_SET_C_FWD = 9  # Set motor 3 PWM rate in a forwards direction
COMMAND_SET_C_REV = 10  # Set motor 3 PWM rate in a reverse direction
COMMAND_GET_C = 11  # Get motor 3 direction and PWM rate
COMMAND_SET_D_FWD = 12  # Set motor 4 PWM rate in a forwards direction
COMMAND_SET_D_REV = 13  # Set motor 4 PWM rate in a reverse direction
COMMAND_GET_D = 14  # Get motor 4 direction and PWM rate
COMMAND_ALL_OFF = 15  # Switch everything off
COMMAND_SET_ALL_FWD = 16  # Set all motors PWM rate in a forwards direction
COMMAND_SET_ALL_REV = 17  # Set all motors PWM rate in a reverse direction
COMMAND_SET_FAILSAFE = 18  # Set the failsafe flag, turns the motors off if communication is interrupted
COMMAND_GET_FAILSAFE = 19  # Get the failsafe flag
COMMAND_RESET_EPO = 20  # Resets the EPO flag, use after EPO has been tripped and switch is now clear
COMMAND_GET_EPO = 21  # Get the EPO latched flag
COMMAND_SET_EPO_IGNORE = 22  # Set the EPO ignored flag, allows the system to run without an EPO
COMMAND_GET_EPO_IGNORE = 23  # Get the EPO ignored flag
COMMAND_GET_NEW_IR = 24  # Get the new IR message received flag
COMMAND_GET_LAST_IR = 25  # Get the last IR message received (long message, resets new IR flag)
COMMAND_SET_LED_IR = 26  # Set the LED for indicating IR messages
COMMAND_GET_LED_IR = 27  # Get if the LED is being used to indicate IR messages
COMMAND_GET_ANALOG_1 = 28  # Get the analog reading from port #1, pin 2
COMMAND_GET_ANALOG_2 = 29  # Get the analog reading from port #2, pin 4
COMMAND_GET_ID = 0x99  # Get the board identifier
COMMAND_SET_I2C_ADD = 0xAA  # Set a new I2C address

COMMAND_VALUE_FWD = 1  # I2C value representing forward
COMMAND_VALUE_REV = 2  # I2C value representing reverse

COMMAND_VALUE_ON = 1  # I2C value representing on
COMMAND_VALUE_OFF = 0  # I2C value representing off

COMMAND_ANALOG_MAX = 0x3FF  # Maximum value for analog readings

IR_MAX_BYTES = I2C_LONG_LEN - 2


# noinspection PyPep8Naming
def ScanForZeroBorg(busNumber=1):
    """
ScanForZeroBorg([busNumber])

Scans the I?C bus for a ZeroBorg boards and returns a list of all usable addresses
The busNumber if supplied is which I?C bus to scan, 0 for Rev 1 boards, 1 for Rev 2 boards, if not supplied
the default is 1
    """
    found = []
    print('Scanning I?C bus #%d' % busNumber)
    bus = ZeroBorg()
    for address in range(0x03, 0x78, 1):
        try:
            bus.InitBusOnly(busNumber, address)
            i2cRecv = bus.RawRead(COMMAND_GET_ID, I2C_NORM_LEN)
            if len(i2cRecv) == I2C_NORM_LEN:
                if i2cRecv[1] == I2C_ID_ZEROBORG:
                    print('Found ZeroBorg at %02X' % address)
                    found.append(address)
                else:
                    pass
            else:
                pass
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print('Error on ZeroBorg scan: {}: {}'.format(type(e), str(e)))

    if len(found) == 0:
        print('No ZeroBorg boards found, is bus #%d correct (should be 0 for Rev 1, 1 for Rev 2)' % busNumber)
    elif len(found) == 1:
        print('1 ZeroBorg board found')
    else:
        print('%d ZeroBorg boards found' % (len(found)))
    return found


# noinspection PyPep8Naming
def SetNewAddress(newAddress, oldAddress=-1, busNumber=1):
    """
SetNewAddress(newAddress, [oldAddress], [busNumber])

Scans the I?C bus for the first ZeroBorg and sets it to a new I2C address
If oldAddress is supplied it will change the address of the board at that address rather than scanning the bus
The busNumber if supplied is which I?C bus to scan, 0 for Rev 1 boards, 1 for Rev 2 boards, if not supplied
the default is 1.
Warning, this new I?C address will still be used after resetting the power on the device
    """
    if newAddress < 0x03:
        print('Error, I?C addresses below 3 (0x03) are reserved, use an address between 3 (0x03) and 119 (0x77)')
        return
    elif newAddress > 0x77:
        print('Error, I?C addresses above 119 (0x77) are reserved, use an address between 3 (0x03) and 119 (0x77)')
        return
    if oldAddress < 0x0:
        found = ScanForZeroBorg(busNumber)
        if len(found) < 1:
            print('No ZeroBorg boards found, cannot set a new I?C address!')
            return
        else:
            oldAddress = found[0]
    print('Changing I2C address from %02X to %02X (bus #%d)' % (oldAddress, newAddress, busNumber))
    bus = ZeroBorg()
    bus.InitBusOnly(busNumber, oldAddress)
    # noinspection PyBroadException
    try:
        i2cRecv = bus.RawRead(COMMAND_GET_ID, I2C_NORM_LEN)
        if len(i2cRecv) == I2C_NORM_LEN:
            if i2cRecv[1] == I2C_ID_ZEROBORG:
                foundChip = True
                print('Found ZeroBorg at %02X' % oldAddress)
            else:
                foundChip = False
                print('Found a device at %02X, but it is not a ZeroBorg (ID %02X instead of %02X)' % (
                    oldAddress, i2cRecv[1], I2C_ID_ZEROBORG))
        else:
            foundChip = False
            print('Missing ZeroBorg at %02X' % oldAddress)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        foundChip = False
        print(str(e))
        print('Missing ZeroBorg at %02X' % oldAddress)
    if foundChip:
        bus.RawWrite(COMMAND_SET_I2C_ADD, [newAddress])
        time.sleep(0.1)
        print('Address changed to %02X, attempting to talk with the new address' % newAddress)
        # noinspection PyBroadException
        try:
            bus.InitBusOnly(busNumber, newAddress)
            i2cRecv = bus.RawRead(COMMAND_GET_ID, I2C_NORM_LEN)
            if len(i2cRecv) == I2C_NORM_LEN:
                if i2cRecv[1] == I2C_ID_ZEROBORG:
                    foundChip = True
                    print('Found ZeroBorg at %02X' % newAddress)
                else:
                    foundChip = False
                    print('Found a device at %02X, but it is not a ZeroBorg (ID %02X instead of %02X)' % (
                        newAddress, i2cRecv[1], I2C_ID_ZEROBORG))
            else:
                foundChip = False
                print('Missing ZeroBorg at %02X' % newAddress)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            foundChip = False
            print(str(e))
            print('Missing ZeroBorg at %02X' % newAddress)
    if foundChip:
        print('New I?C address of %02X set successfully' % newAddress)
    else:
        print('Failed to set new I?C address...')


# Class used to control ZeroBorg
# noinspection PyPep8Naming
class ZeroBorg:
    """
This module is designed to communicate with the ZeroBorg

busNumber               I?C bus on which the ZeroBorg is attached (Rev 1 is bus 0, Rev 2 is bus 1)
bus                     the smbus object used to talk to the I?C bus
i2cAddress              The I?C address of the ZeroBorg chip to control
foundChip               True if the ZeroBorg chip can be seen, False otherwise
printFunction           Function reference to call when printing text, if None "print" is used
    """

    # Shared values used by this class
    busNumber = 1  # Check here for Rev 1 vs Rev 2 and select the correct bus
    i2cAddress = I2C_ID_ZEROBORG  # I?C address, override for a different address
    foundChip = False
    printFunction = None
    i2cWrite = None
    i2cRead = None

    def RawWrite(self, command, data):
        """
RawWrite(command, data)

Sends a raw command on the I2C bus to the ZeroBorg
Command codes can be found at the top of ZeroBorg.py, data is a list of 0 or more byte values

Under most circumstances you should use the appropriate function instead of RawWrite
        """
        rawOutput = bytes([command])
        if data:
            rawOutput += bytes(data)
        self.i2cWrite.write(rawOutput)

    def RawRead(self, command, length, retryCount=3):
        """
RawRead(command, length, [retryCount])

Reads data back from the ZeroBorg after sending a GET command
Command codes can be found at the top of ZeroBorg.py, length is the number of bytes to read back

The function checks that the first byte read back matches the requested command
If it does not it will retry the request until retryCount is exhausted (default is 3 times)

Under most circumstances you should use the appropriate function instead of RawRead
        """
        reply = []

        while retryCount > 0:
            self.RawWrite(command, [])
            rawReply = self.i2cRead.read(length)
            reply = []
            for singleByte in rawReply:
                reply.append(singleByte)
            if command == reply[0]:
                break
            else:
                retryCount -= 1
        if retryCount > 0:
            return reply
        else:
            raise IOError('I2C read for command %d failed' % command)

    def InitBusOnly(self, busNumber, address):
        """
InitBusOnly(busNumber, address)

Prepare the I2C driver for talking to a ZeroBorg on the specified bus and I2C address
This call does not check the board is present or working, under most circumstances use Init() instead
        """
        self.busNumber = busNumber
        self.i2cAddress = address
        self.i2cRead = io.open("/dev/i2c-" + str(self.busNumber), "rb", buffering=0)
        fcntl.ioctl(self.i2cRead, I2C_SLAVE, self.i2cAddress)
        self.i2cWrite = io.open("/dev/i2c-" + str(self.busNumber), "wb", buffering=0)
        fcntl.ioctl(self.i2cWrite, I2C_SLAVE, self.i2cAddress)

    def Print(self, message):
        """
Print(message)

Wrapper used by the ZeroBorg instance to print messages, will call printFunction if set, print otherwise
        """
        if self.printFunction is None:
            print(message)
        else:
            self.printFunction(message)

    def NoPrint(self, message):
        """
NoPrint(message)

Does nothing, intended for disabling diagnostic printout by using:
ZB = ZeroBorg.ZeroBorg()
ZB.printFunction = ZB.NoPrint
        """
        pass

    def Init(self, tryOtherBus=False):
        """
Init([tryOtherBus])

Prepare the I2C driver for talking to the ZeroBorg

If tryOtherBus is True, this function will attempt to use the other bus if the ThunderBorg devices can not be found on
the current busNumber.

    This is only really useful for early Raspberry Pi models!
        """
        self.Print('Loading ZeroBorg on bus %d, address %02X' % (self.busNumber, self.i2cAddress))

        # Open the bus
        self.i2cRead = io.open("/dev/i2c-" + str(self.busNumber), "rb", buffering=0)
        fcntl.ioctl(self.i2cRead, I2C_SLAVE, self.i2cAddress)
        self.i2cWrite = io.open("/dev/i2c-" + str(self.busNumber), "wb", buffering=0)
        fcntl.ioctl(self.i2cWrite, I2C_SLAVE, self.i2cAddress)

        # Check for ZeroBorg
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_ID, I2C_NORM_LEN)
            if len(i2cRecv) == I2C_NORM_LEN:
                if i2cRecv[1] == I2C_ID_ZEROBORG:
                    self.foundChip = True
                    self.Print('Found ZeroBorg at %02X' % self.i2cAddress)
                else:
                    self.foundChip = False
                    self.Print('Found a device at %02X, but it is not a ZeroBorg (ID %02X instead of %02X)' % (
                        self.i2cAddress, i2cRecv[1], I2C_ID_ZEROBORG))
            else:
                self.foundChip = False
                self.Print('Missing ZeroBorg at %02X' % self.i2cAddress)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.foundChip = False
            self.Print('Missing ZeroBorg at %02X: %s' % (self.i2cAddress, str(e)))

        # See if we are missing chips
        if not self.foundChip:
            self.Print('ZeroBorg was not found')
            if tryOtherBus:
                if self.busNumber == 1:
                    self.busNumber = 0
                else:
                    self.busNumber = 1
                self.Print('Trying bus %d instead' % self.busNumber)
                self.Init(False)
            else:
                self.Print(
                    'Are you sure your ZeroBorg is properly attached, the correct address is used, and the I2C ' +
                    'drivers are running?')
                self.bus = None
        else:
            self.Print('ZeroBorg loaded on bus %d' % self.busNumber)

    def SetMotor1(self, power):
        """
SetMotor1(power)

Sets the drive level for motor 1, from +1 to -1.
e.g.
SetMotor1(0)     -> motor 1 is stopped
SetMotor1(0.75)  -> motor 1 moving forward at 75% power
SetMotor1(-0.5)  -> motor 1 moving reverse at 50% power
SetMotor1(1)     -> motor 1 moving forward at 100% power
        """
        if power < 0:
            # Reverse
            command = COMMAND_SET_A_REV
            pwm = -int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX
        else:
            # Forward / stopped
            command = COMMAND_SET_A_FWD
            pwm = int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX

        # noinspection PyBroadException
        try:
            self.RawWrite(command, [pwm])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending motor 1 drive level! {}'.format(str(e)))

    def GetMotor1(self):
        """
power = GetMotor1()

Gets the drive level for motor 1, from +1 to -1.
e.g.
0     -> motor 1 is stopped
0.75  -> motor 1 moving forward at 75% power
-0.5  -> motor 1 moving reverse at 50% power
1     -> motor 1 moving forward at 100% power
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_A, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading motor 1 drive level! {}'.format(str(e)))
            return

        power = float(i2cRecv[2]) / float(PWM_MAX)

        if i2cRecv[1] == COMMAND_VALUE_FWD:
            return power
        elif i2cRecv[1] == COMMAND_VALUE_REV:
            return -power
        else:
            return

    def SetMotor2(self, power):
        """
SetMotor1(power)

Sets the drive level for motor 2, from +1 to -1.
e.g.
SetMotor2(0)     -> motor 2 is stopped
SetMotor2(0.75)  -> motor 2 moving forward at 75% power
SetMotor2(-0.5)  -> motor 2 moving reverse at 50% power
SetMotor2(1)     -> motor 2 moving forward at 100% power
        """
        if power < 0:
            # Reverse
            command = COMMAND_SET_B_REV
            pwm = -int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX
        else:
            # Forward / stopped
            command = COMMAND_SET_B_FWD
            pwm = int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX

        # noinspection PyBroadException
        try:
            self.RawWrite(command, [pwm])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending motor 2 drive level! {}'.format(str(e)))

    def GetMotor2(self):
        """
power = GetMotor2()

Gets the drive level for motor 2, from +1 to -1.
e.g.
0     -> motor 2 is stopped
0.75  -> motor 2 moving forward at 75% power
-0.5  -> motor 2 moving reverse at 50% power
1     -> motor 2 moving forward at 100% power
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_B, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading motor 2 drive level! {}'.format(str(e)))
            return

        power = float(i2cRecv[2]) / float(PWM_MAX)

        if i2cRecv[1] == COMMAND_VALUE_FWD:
            return power
        elif i2cRecv[1] == COMMAND_VALUE_REV:
            return -power
        else:
            return

    def SetMotor3(self, power):
        """
SetMotor3(power)

Sets the drive level for motor 3, from +1 to -1.
e.g.
SetMotor3(0)     -> motor 3 is stopped
SetMotor3(0.75)  -> motor 3 moving forward at 75% power
SetMotor3(-0.5)  -> motor 3 moving reverse at 50% power
SetMotor3(1)     -> motor 3 moving forward at 100% power
        """
        if power < 0:
            # Reverse
            command = COMMAND_SET_C_REV
            pwm = -int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX
        else:
            # Forward / stopped
            command = COMMAND_SET_C_FWD
            pwm = int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX

        # noinspection PyBroadException
        try:
            self.RawWrite(command, [pwm])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending motor 3 drive level! {}'.format(str(e)))

    def GetMotor3(self):
        """
power = GetMotor3()

Gets the drive level for motor 3, from +1 to -1.
e.g.
0     -> motor 3 is stopped
0.75  -> motor 3 moving forward at 75% power
-0.5  -> motor 3 moving reverse at 50% power
1     -> motor 3 moving forward at 100% power
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_C, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading motor 3 drive level! {}'.format(str(e)))
            return

        power = float(i2cRecv[2]) / float(PWM_MAX)

        if i2cRecv[1] == COMMAND_VALUE_FWD:
            return power
        elif i2cRecv[1] == COMMAND_VALUE_REV:
            return -power
        else:
            return

    def SetMotor4(self, power):
        """
SetMotor4(power)

Sets the drive level for motor 4, from +1 to -1.
e.g.
SetMotor4(0)     -> motor 4 is stopped
SetMotor4(0.75)  -> motor 4 moving forward at 75% power
SetMotor4(-0.5)  -> motor 4 moving reverse at 50% power
SetMotor4(1)     -> motor 4 moving forward at 100% power
        """
        if power < 0:
            # Reverse
            command = COMMAND_SET_D_REV
            pwm = -int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX
        else:
            # Forward / stopped
            command = COMMAND_SET_D_FWD
            pwm = int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX

        # noinspection PyBroadException
        try:
            self.RawWrite(command, [pwm])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending motor 4 drive level! {}'.format(str(e)))

    def GetMotor4(self):
        """
power = GetMotor4()

Gets the drive level for motor 4, from +1 to -1.
e.g.
0     -> motor 4 is stopped
0.75  -> motor 4 moving forward at 75% power
-0.5  -> motor 4 moving reverse at 50% power
1     -> motor 4 moving forward at 100% power
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_D, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading motor 4 drive level! {}'.format(str(e)))
            return

        power = float(i2cRecv[2]) / float(PWM_MAX)

        if i2cRecv[1] == COMMAND_VALUE_FWD:
            return power
        elif i2cRecv[1] == COMMAND_VALUE_REV:
            return -power
        else:
            return

    def SetMotors(self, power):
        """
SetMotors(power)

Sets the drive level for all motors, from +1 to -1.
e.g.
SetMotors(0)     -> all motors are stopped
SetMotors(0.75)  -> all motors are moving forward at 75% power
SetMotors(-0.5)  -> all motors are moving reverse at 50% power
SetMotors(1)     -> all motors are moving forward at 100% power
        """
        if power < 0:
            # Reverse
            command = COMMAND_SET_ALL_REV
            pwm = -int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX
        else:
            # Forward / stopped
            command = COMMAND_SET_ALL_FWD
            pwm = int(PWM_MAX * power)
            if pwm > PWM_MAX:
                pwm = PWM_MAX

        # noinspection PyBroadException
        try:
            self.RawWrite(command, [pwm])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending all motors drive level! {}'.format(str(e)))

    def MotorsOff(self):
        """
MotorsOff()

Sets all motors to stopped, useful when ending a program
        """
        # noinspection PyBroadException
        try:
            self.RawWrite(COMMAND_ALL_OFF, [0])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending motors off command! {}'.format(str(e)))

    def SetLed(self, state):
        """
SetLed(state)

Sets the current state of the LED, False for off, True for on
        """
        if state:
            level = COMMAND_VALUE_ON
        else:
            level = COMMAND_VALUE_OFF

        try:
            self.RawWrite(COMMAND_SET_LED, [level])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending LED state!')
            self.Print(e)

    def GetLed(self):
        """
state = GetLed()

Reads the current state of the LED, False for off, True for on
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_LED, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading LED state! {}'.format(str(e)))
            return

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def ResetEpo(self):
        """
ResetEpo()

Resets the EPO latch state, use to allow movement again after the EPO has been tripped
        """
        # noinspection PyBroadException
        try:
            self.RawWrite(COMMAND_RESET_EPO, [0])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed resetting EPO! {}'.format(str(e)))

    def GetEpo(self):
        """
state = GetEpo()

Reads the system EPO latch state.
If False the EPO has not been tripped, and movement is allowed.
If True the EPO has been tripped, movement is disabled if the EPO is not ignored (see SetEpoIgnore)
    Movement can be re-enabled by calling ResetEpo.
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_EPO, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading EPO ignore state! {}'.format(str(e)))
            return

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def SetEpoIgnore(self, state):
        """
SetEpoIgnore(state)

Sets the system to ignore or use the EPO latch, set to False if you have an EPO switch, True if you do not
        """
        if state:
            level = COMMAND_VALUE_ON
        else:
            level = COMMAND_VALUE_OFF

        # noinspection PyBroadException
        try:
            self.RawWrite(COMMAND_SET_EPO_IGNORE, [level])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending EPO ignore state! {}'.format(str(e)))

    def GetEpoIgnore(self):
        """
state = GetEpoIgnore()

Reads the system EPO ignore state, False for using the EPO latch, True for ignoring the EPO latch
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_EPO_IGNORE, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading EPO ignore state! {}'.format(str(e)))
            return

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def HasNewIrMessage(self):
        """
state = HasNewIrMessage()

Reads the new IR message received flag.
If False there has been no messages to the IR sensor since the last read.
If True there has been a new IR message which can be read using GetIrMessage().
        """
        try:
            i2cRecv = self.RawRead(COMMAND_GET_NEW_IR, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading new IR message received flag!')
            raise e

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def GetIrMessage(self):
        """
message = GetIrMessage()

Reads the last IR message which has been received and clears the new IR message received flag.
Returns the bytes from the remote control as a hexadecimal string, e.g. 'F75AD5AA8000'
Use HasNewIrMessage() to see if there has been a new IR message since the last call.
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_LAST_IR, I2C_LONG_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading IR message! {}'.format(str(e)))
            return

        message = ''
        for i in range(IR_MAX_BYTES):
            message += '%02X' % (i2cRecv[1 + i])
        return message.rstrip('0')

    def SetLedIr(self, state):
        """
SetLedIr(state)

Sets if IR messages control the state of the LED, False for no effect, True for incoming messages blink the LED
        """
        if state:
            level = COMMAND_VALUE_ON
        else:
            level = COMMAND_VALUE_OFF

        # noinspection PyBroadException
        try:
            self.RawWrite(COMMAND_SET_LED_IR, [level])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending LED state! {}'.format(str(e)))

    def GetLedIr(self):
        """
state = GetLedIr()

Reads if IR messages control the state of the LED, False for no effect, True for incoming messages blink the LED
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_LED_IR, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading LED state! {}'.format(str(e)))
            return

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def GetAnalog1(self):
        """
voltage = GetAnalog1()

Reads the current analog level from port #1 (pin 2).
Returns the value as a voltage based on the 3.3 V reference pin (pin 1).
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_ANALOG_1, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading analog level #1! {}'.format(str(e)))
            return

        raw = (i2cRecv[1] << 8) + i2cRecv[2]
        level = float(raw) / float(COMMAND_ANALOG_MAX)
        return level * 3.3

    def GetAnalog2(self):
        """
voltage = GetAnalog2()

Reads the current analog level from port #2 (pin 4).
Returns the value as a voltage based on the 3.3 V reference pin (pin 1).
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_ANALOG_2, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading analog level #2! {}'.format(str(e)))
            return

        raw = (i2cRecv[1] << 8) + i2cRecv[2]
        level = float(raw) / float(COMMAND_ANALOG_MAX)
        return level * 3.3

    def SetCommsFailsafe(self, state):
        """
SetCommsFailsafe(state)

Sets the system to enable or disable the communications failsafe
The failsafe will turn the motors off unless it is commanded at least once every 1/4 of a second
Set to True to enable this failsafe, set to False to disable this failsafe
The failsafe is disabled at power on
        """
        if state:
            level = COMMAND_VALUE_ON
        else:
            level = COMMAND_VALUE_OFF

        # noinspection PyBroadException
        try:
            self.RawWrite(COMMAND_SET_FAILSAFE, [level])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed sending communications failsafe state! {}'.format(str(e)))

    def GetCommsFailsafe(self):
        """
state = GetCommsFailsafe()

Read the current system state of the communications failsafe, True for enabled, False for disabled
The failsafe will turn the motors off unless it is commanded at least once every 1/4 of a second
        """
        # noinspection PyBroadException
        try:
            i2cRecv = self.RawRead(COMMAND_GET_FAILSAFE, I2C_NORM_LEN)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.Print('Failed reading communications failsafe state! {}'.format(str(e)))
            return

        if i2cRecv[1] == COMMAND_VALUE_OFF:
            return False
        else:
            return True

    def Help(self):
        """
Help()

Displays the names and descriptions of the various functions and settings provided
        """
        # noinspection PyTypeChecker
        funcList = [ZeroBorg.__dict__.get(a) for a in dir(ZeroBorg) if
                    isinstance(ZeroBorg.__dict__.get(a), types.FunctionType)]
        funcListSorted = sorted(funcList, key=lambda x: x.func_code.co_firstlineno)

        print(self.__doc__)
        print()
        for func in funcListSorted:
            print('=== %s === %s' % (func.func_name, func.func_doc))
