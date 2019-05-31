#!/usr/local/bin/python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <phk@FreeBSD.ORG> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp
# ----------------------------------------------------------------------------
#

from __future__ import print_function

# You need pySerial
import serial

import math

import logging
logging.basicConfig(level=logging.DEBUG)

from optparse import OptionParser

#######################################################################
# These are the variables I have managed to identify
# Submissions welcome.

kamstrup_382_var = {

    0x0001: "Energy-in-low-res",
    0x0002: "Energy-out-low-res",

    0x000d: "Ap",
    0x000e: "Am",

    0x041e: "U1",
    0x041f: "U2",
    0x0420: "U3",

    0x0434: "I1",
    0x0435: "I2",
    0x0436: "I3",

    0x0438: "P1",
    0x0439: "P2",
    0x043a: "P3",
    0x03e9: 'Meter-serialnumber',  # not user configurable
    #0x0033:  'Meter-number',        # user configurable
    #0x04f4: 'M-bus-address',
}

kamstrup_162J_var = {

    0x0001: "Energy-in-low-res",
    0x0002: "Energy-out-low-res",

    0x000d: "Ap",
    0x000e: "Am",

    0x041e: "U1",

    0x0434: "I1",

    0x0438: "P1",
    0x03e9: 'Meter-serialnumber',
}

kamstrup_362J_var = {

    0x0001: "Energy-in-low-res",
    0x0002: "Energy-out-low-res",

    0x000d: "Ap",
    0x000e: "Am",

    0x041e: "U1",
    0x041f: "U2",
    0x0420: "U3",

    0x0434: "I1",
    0x0435: "I2",
    0x0436: "I3",

    0x0438: "P1",
    0x0439: "P2",
    0x043a: "P3",
    0x03e9: 'Meter-serialnumber',
}

kamstrup_684_var = {
    0x0032: "unknown", # unit 51
    0x0033: "SerialNo", # unit 51 1.1.96.1.0.255
    0x0034: "unknown", # unit 51
    0x0035: "unknown", # unit 51
    0x03e9: "unknown", # unit 51
    0x03f2: "unknown", # unit 51
    0x0406: "unknown", # unit 51
    0x0417: "unknown", # unit 53
    0x043b: "unknown", # unit 51
    0x0466: "CompleteMeterTypeNo", # unit 54 1.1.96.1.1.255
    0x04c5: "unknown", # unit 0
    0x04db: "unknown", # unit 0
    0x0620: "unknown", # unit 54
    0x062b: "unknown", # unit 0
    0x178a: "unknown", # unit 51
    0x178e: "unknown", # unit 54
    0x178f: "unknown", # unit 54
    0x180d: "unknown", # unit 0
    0x180e: "unknown", # unit 51
    0x1824: "unknown", # unit 51
    0x1845: "unknown", # unit 54
    0x1867: "IdentificationNumber", # unit 54 1.1.0.0.4.255
    0x186c: "unknown", # unit 0
    0x1874: "unknown", # unit 51
    0x1875: "unknown", # unit 54
    0x1876: "unknown", # unit 51
    0x1880: "unknown", # unit 51
    0x1885: "unknown", # unit 51
    0x1886: "unknown", # unit 51
    0x1887: "unknown", # unit 51
    0x1888: "unknown", # unit 51
    0x1889: "unknown", # unit 51
    0x188a: "unknown", # unit 51
    0x188b: "unknown", # unit 51
    0x188c: "unknown", # unit 51
    0x188d: "unknown", # unit 51
    0x188e: "unknown", # unit 51
    0x188f: "unknown", # unit 51
    0x1890: "unknown", # unit 51
    0x1893: "unknown", # unit 51
    0x1894: "unknown", # unit 51
    0x18a0: "unknown", # unit 51
    0x18ad: "unknown", # unit 0
    0x18ae: "unknown", # unit 0
    0x18af: "unknown", # unit 0
    0x18b0: "unknown", # unit 0
    0x18b1: "unknown", # unit 0
    0x18b2: "unknown", # unit 0
    0x18b3: "unknown", # unit 0
    0x18b4: "unknown", # unit 0
}

# to scan the entire address space
kamstrup_scan_var = {
    x: "unknown" for x in range(0x0001,0xffff)
}

#######################################################################
# Units, provided by Erik Jensen

units = {
    0: '', 1: 'Wh', 2: 'kWh', 3: 'MWh', 4: 'GWh', 5: 'j', 6: 'kj', 7: 'Mj',
    8: 'Gj', 9: 'Cal', 10: 'kCal', 11: 'Mcal', 12: 'Gcal', 13: 'varh',
    14: 'kvarh', 15: 'Mvarh', 16: 'Gvarh', 17: 'VAh', 18: 'kVAh',
    19: 'MVAh', 20: 'GVAh', 21: 'kW', 22: 'kW', 23: 'MW', 24: 'GW',
    25: 'kvar', 26: 'kvar', 27: 'Mvar', 28: 'Gvar', 29: 'VA', 30: 'kVA',
    31: 'MVA', 32: 'GVA', 33: 'V', 34: 'A', 35: 'kV',36: 'kA', 37: 'C',
    38: 'K', 39: 'l', 40: 'm3', 41: 'l/h', 42: 'm3/h', 43: 'm3xC',
    44: 'ton', 45: 'ton/h', 46: 'h', 47: 'hh:mm:ss', 48: 'yy:mm:dd',
    49: 'yyyy:mm:dd', 50: 'mm:dd', 51: '', 52: 'bar', 53: 'RTC',
    54: 'ASCII', 55: 'm3 x 10', 56: 'ton x 10', 57: 'GJ x 10',
    58: 'minutes', 59: 'Bitfield', 60: 's', 61: 'ms', 62: 'days',
    63: 'RTC-Q', 64: 'Datetime'
}

#######################################################################
# Kamstrup uses the "true" CCITT CRC-16
#

def crc_1021(message):
        poly = 0x1021
        reg = 0x0000
        for byte in message:
                mask = 0x80
                while(mask > 0):
                        reg<<=1
                        if byte & mask:
                                reg |= 1
                        mask>>=1
                        if reg & 0x10000:
                                reg &= 0xffff
                                reg ^= poly
        return reg

#######################################################################
# Byte values which must be escaped before transmission
#

escapes = {
    0x06: True,
    0x0d: True,
    0x1b: True,
    0x40: True,
    0x80: True,
}

#######################################################################
# And here we go....
#
class kamstrup(object):

    def __init__(self, serial_port = "/dev/ttyUSB0"):
        # due to the way the file is written we cannot use the logging framework for the debug log
        self.debug_fd = open("/tmp/kamstrup.log", "a")
        self.debug_fd.write("\n\nStart\n")
        self.debug_id = None

        # open the serial port
        self.ser = serial.Serial(
            port = serial_port,
            baudrate = 9600,
            timeout = 1.0
        )

    def debug(self, direction, b):
        """
        Debug log some data on the wire
        """
        # are we still logging in the same direction?
        if direction != self.debug_id:
            if self.debug_id != None:
                self.debug_fd.write("\n")
                self.debug_fd.write(direction + "\t")
            self.debug_id = direction
        # loop over the bytes and output each as HEX
        for i in b:
            self.debug_fd.write(" %02x " % i)
        # make sure we can see the data right away
        self.debug_fd.flush()

    def debug_msg(self, msg):
        """
        Debug logs a regular message (not data on the wire)
        """
        if self.debug_id != None:
            self.debug_fd.write("\n")
        self.debug_id = "Msg"
        self.debug_fd.write("Msg\t" + msg)
        self.debug_fd.flush()

    def wr(self, b):
        b = bytearray(b)
        self.debug("Wr", b);
        self.ser.write(b)

    def rd(self):
        a = self.ser.read(1)
        if len(a) == 0:
            self.debug_msg("Rx Timeout")
            return None
        b = bytearray(a)[0]
        self.debug("Rd", bytearray((b,)));
        return b

    def send(self, pfx, msg):
        b = bytearray(msg)

        b.append(0)
        b.append(0)
        c = crc_1021(b)
        b[-2] = c >> 8
        b[-1] = c & 0xff

        c = bytearray()
        c.append(pfx)
        for i in b:
            if i in escapes:
                c.append(0x1b)
                c.append(i ^ 0xff)
            else:
                c.append(i)
        c.append(0x0d)
        self.wr(c)

    def recv(self):
        b = bytearray()
        while True:
            d = self.rd()
            if d == None:
                return None
            if d == 0x40:
                b = bytearray()
            b.append(d)
            if d == 0x0d:
                break
        c = bytearray()
        i = 1;
        while i < len(b) - 1:
            if b[i] == 0x1b:
                v = b[i + 1] ^ 0xff
                if v not in escapes:
                    self.debug_msg(
                        "Missing Escape %02x" % v)
                c.append(v)
                i += 2
            else:
                c.append(b[i])
                i += 1
        if crc_1021(c):
            self.debug_msg("CRC error")
        return c[:-2]

    def readvar(self, nbr):
        # I wouldn't be surprised if you can ask for more than
        # one variable at the time, given that the length is
        # encoded in the response.  Havn't tried.

        self.send(0x80, (0x3f, 0x10, 0x01, nbr >> 8, nbr & 0xff))

        b = self.recv()
        if b == None:
            logging.error("No data returned for register %s" % nbr)
            return (None, None)

        # why must everything begin with 3f 10 (byte 1 and 2)
        if b[0] != 0x3f or b[1] != 0x10:
            logging.error("Data does not begin with 3f 10")
            return (None, None)

        # check that the response if for the register we asked about (byte 3 and 4)
        if b[2] != nbr >> 8 or b[3] != nbr & 0xff:
            logging.error("Response for register %s when asking for %s" % (nbr, b[2:3]))
            return (None, None)

        # Lookup unit type (byte 5)
        unit = units.get(b[4], None)

        # Decode the payload length (byte 6) and the payload (byte 8 and onwards)
        x = 0
        for i in range(0,b[5]):
            x <<= 8
            x |= b[i + 7]

        # Decode the exponent/scaling factor (byte 7)
        i = b[6] & 0x3f
        if b[6] & 0x40:
            i = -i
        i = math.pow(10,i)
        if b[6] & 0x80:
            i = -i
        # scale it
        x *= i

        if True:
            # Debug print
            s = ""
            # 3f 10 and register address
            for i in b[:4]:
                s += " %02x" % i
            s += " |"
            # unit, length, factor
            for i in b[4:7]:
                s += " %02x" % i
            s += " |"
            s2 = ""
            # data
            for i in b[7:]:
                s += " %02x" % i
                s2 += " %02x" % i
            print(s, "=", x, units[b[4]])
            if unit=="ASCII":
                print(bytearray.fromhex(s2).decode('ascii'))

        return (x, unit)


if __name__ == "__main__":

    import time
    import datetime

    parser = OptionParser()
    parser.add_option(
        "-s", "--serial_port",
        dest="serial_port",
        help="Specify serial device path.",
        metavar="SERIAL_PORT",
        default="/dev/ttyUSB0",
        type="string",
    )
    parser.add_option(
        "-m", "--meter_type",
        dest="meter_type",
        help="Specify Kamstrup meter type.",
        metavar="METER_TYPE",
        default="162J",
        choices=["162J","362J","382","684","scan"],
    )
    (options, args) = parser.parse_args()

    foo = kamstrup(serial_port=options.serial_port)

    meter_type_str=str(options.meter_type)

    if meter_type_str in "162J":
        meter_type_var=kamstrup_162J_var
    elif meter_type_str in "362J":
        meter_type_var=kamstrup_362J_var
    elif meter_type_str in "382":
        meter_type_var=kamstrup_382_var
    elif meter_type_str in "684":
        meter_type_var=kamstrup_684_var
    elif meter_type_str in "scan":
        meter_type_var=kamstrup_scan_var
    else:
        raise ValueError("ERROR: Meter type not defined!")


    print("%-25s"%"Time",time.strftime("%H:%M:%S"),"Time")
    print("%-25s"%"Date",datetime.date.today().strftime("%m/%d/%Y"),"Date")
    for i in meter_type_var:
        try:
            x, u = foo.readvar(i)
        except IndexError:
            # this register does not exist on this meter
            continue
        mtv=meter_type_var[i]
        if 'I1' in mtv or 'I2' in mtv or 'I3' in mtv:
                print(hex(i), "%-25s" % meter_type_var[i], x*1000, 'mA')
        else:
                print(hex(i), "%-25s" % meter_type_var[i], x, u)
        print("----------------------------")

