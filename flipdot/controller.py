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

import serial
import time
from PIL import Image, ImageDraw, ImageFont

from .utils import *

class MatrixError(Exception):
    ERR_CODES = {
        0xE0: "Timeout",
        0xEE: "Generic Error",
        0xFF: "Success",
          -1: "No response from controller"
    }

    def __init__(self, code = None, response = None):
        if code is None:
            if response:
                self.code = response
            else:
                self.code = -1
        else:
            self.code = code
        self.description = self.ERR_CODES.get(self.code, "Unknown Error")
    
    def __str__(self):
        return "{0}: {1}".format(self.code, self.description)

class FlipdotController(object):
    def __init__(self, port, width, height = 16, using_mux = False, mux_port = 0):
        self.port = port
        self.width = width
        self.height = height
        self.using_mux = using_mux
        self.mux_port = mux_port
        self.message = bytearray()
        self.ser = get_serial_port(port)

    def write(self, data):
        if type(data) is int:
            data = bytes([data])
        self.ser.write(data)

    def communicate(self):
        if self.using_mux:
            self.init_mux_message()
        self.write(self.message)
        return self.check_status()

    def check_status(self):
        status = self.ser.read(1)
        if status:
            status = ord(status)
        else:
            status = 0
        if status != 0xFF:
            raise MatrixError(response = status)
        return status

    def init_mux_message(self):
        # If an Arduino-based serial port muxer is used, this is used to add mux control data to every sent message
        self.write(0xF0)
        self.write(0xC0 + self.mux_port)
        len_msb = len(self.message) >> 8
        len_lsb = len(self.message) & 0xFF
        self.write(len_msb)
        self.write(len_lsb)

    def prepare_message(self, *args):
        self.message = bytearray([0xFF])
        for arg in args:
            if type(arg) is int:
                self.message.append(arg)
            else:
                self.message += bytearray(arg)

    def send_bitmap(self, bitmap):
        if type(bitmap) != bytearray:
            bitmap = bytearray(bitmap)
        # Pad bitmap to display width if necessary to avoid memory contents filling the rest of the display
        if len(bitmap) < 2*self.width:
            bitmap += bytearray([0] * (2*self.width - len(bitmap)))
        self.prepare_message(0xA0, len(bitmap), bitmap)
        return self.communicate()

    def set_backlight(self, state):
        self.prepare_message(0xA1, 0x01 if state else 0x00)
        return self.communicate()

    def set_inverting(self, state):
        self.prepare_message(0xA2, 0x01 if state else 0x00)
        return self.communicate()

    def set_active(self, state):
        self.prepare_message(0xA3, 0x01 if state else 0x00)
        return self.communicate()

    def set_quick_update(self, state):
        self.prepare_message(0xA4, 0x01 if state else 0x00)
        return self.communicate()

class DummyFlipdotController(object):
    """
    A dummy class to use when you want to use FlipdotGraphics, but aren't directly connected to a flipdot controller.
    It has width and height attributes, but can obviously not send data to a display.
    This is useful when you use the client-server system and want to render graphics client-side.
    """

    def __init__(self, width, height = 16):
        self.port = None
        self.width = width
        self.height = height