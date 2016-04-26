#!/usr/bin/env python3
# Copyright (C) 2016 Julian Metzler

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
This program is used to update the Arduino firmware in the flipdot displays using the multiplex module.
A power cycle is needed to run the new firmware.
"""

import argparse
import subprocess
from flipdot.utils import get_serial_port
import time

AVRDUDE_CONF = "avrdude.conf"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type = str, required = True,
        help = "The serial port for communication")
    parser.add_argument('-a', '--address', type = int, required = True,
        help = "The multiplex address of the display to update")
    parser.add_argument('-f', '--firmware', type = str, required = True,
        help = "The hex file to upload")
    args = parser.parse_args()

    port = get_serial_port(args.port)

    # Put the controller in programming mode
    print("Putting controller in programming mode...")
    port.write(bytearray([0xF0, 0xC0+args.address, 0x00, 0x02, 0xFF, 0xAF]))
    status = port.read(1)
    if status:
        print("Response: " + hex(ord(status)))
    else:
        print("No response from controller. Assuming it is already in programming mode.")

    # Set up the multiplexer port for permanent listening
    print("Setting up multiplexer...")
    port.write(bytearray([0xF0, 0xC0+args.address, 0x00, 0x00]))

    # Call avrdude to upload the hex file
    print("Uploading firmware...")
    print("avrdude -C{conf} -v -patmega328p -carduino -P{port} -b57600 -D -Uflash:w:{firmware}:i".format(conf = "avrdude.conf", port = args.port, firmware = args.firmware))
    subprocess.call(["avrdude", "-C"+AVRDUDE_CONF, "-v", "-patmega328p", "-carduino", "-P"+args.port, "-b57600", "-D", "-Uflash:w:"+args.firmware+":i"])

    print("No read-back from controller is normal because of bootloader modifications.")
    print("Firmware updated (hopefully!). Restart multiplexer to update another display, power cycle the display system to run new firmware.")

if __name__ == "__main__":
    main()