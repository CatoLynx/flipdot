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

import datetime
import math
import os
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

class FlipdotGraphics(object):
    DEFAULT_FONT = "FIS_20"
    FONT_DIR = "fonts"

    def __init__(self, controller, verbose = False):
        self.verbose = verbose
        self.controller = controller
        self.init_image()
        self.font_list = {}
        self.load_fonts()

    def output_verbose(self, text):
        if self.verbose:
            print(text)

    def get_bitmap(self):
        return self.image_to_bitmap(self.img)

    def init_image(self):
        self.img = Image.new('L', (self.controller.width, self.controller.height), 'black')
        self.draw = ImageDraw.Draw(self.img)
        self.draw.fontmode = "1"

    def commit(self):
        self.controller.send_bitmap(self.get_bitmap())
        self.init_image()

    def _nice_font_name(self, name):
        name = name.lower()
        name = name.replace(",", " ")
        name = " ".join(sorted(set(name.split())))
        return name
    
    def load_fonts(self):
        def _parse_line(line):
            try:
                path, name, style = [part.strip() for part in line.split(":")]
            except ValueError:
                return (None, None)
            style = style.lower()
            styles = []
            if "bold" in style:
                styles.append("Bold")
            if "italic" in style:
                styles.append("Italic")
            if "narrow" in style:
                styles.append("Narrow")
            if "regular" in style:
                styles.append("Regular")
            if "oblique" in style:
                styles.append("Oblique")
            if "condensed" in style:
                styles.append("Condensed")
            if "black" in style:
                styles.append("Black")
            combined_name = name + " " + " ".join(styles)
            return (path, combined_name)
        
        self.output_verbose("Loading available fonts...")
        raw_list = subprocess.check_output(("fc-list", "-f", "%{file}:%{family}:%{style}\n", ":fontformat=TrueType")).decode('utf-8')
        font_list = dict([_parse_line(line) for line in raw_list.splitlines()])
        for path, name in font_list.items():
            if path and name:
                _name = self._nice_font_name(name)
                self.font_list[_name] = path
        self.output_verbose("Found {0} fonts.".format(len(self.font_list)))
    
    def get_font(self, query):
        # Perform a direct lookup first
        path = self.font_list.get(self._nice_font_name(query))
        if path:
            return path

        # Then check for a font called "... Regular"
        path = self.font_list.get(self._nice_font_name(query + " Regular"))
        if path:
            return path
        else:
            raise ValueError("No font found for query '{0}'.".format(query))

    def get_imagefont(self, font, size = None):
        try:
            # font parameter as ttf filename
            return ImageFont.truetype(font, size), True
        except OSError:
            pass

        try:
            # font parameter as ttf filename in font dir
            _font = font
            if not _font.endswith(".ttf"):
                _font += ".ttf"
            return ImageFont.truetype(os.path.join(self.FONT_DIR, _font), size), True
        except OSError:
            pass

        try:
            # font parameter as PIL bitmap font filename
            _font = font
            if not _font.endswith(".pil"):
                _font += ".pil"
            return ImageFont.load(os.path.join(self.FONT_DIR, _font)), False
        except OSError:
            pass

        try:
            # font parameter as font name
            return ImageFont.truetype(self.get_font(font), size), True
        except (OSError, ValueError):
            pass

        raise ValueError("No font found for query '{0}'.".format(font))

    def image_to_bitmap(self, image):
        if isinstance(image, Image.Image):
            img = image.convert('L')
        else:
            img = Image.open(image).convert('L')
        pixels = img.load()
        width, height = img.size
        bitmap = []
        for x in range(width):
            col_byte = 0x00
            for y in range(height):
                if pixels[x, y] > 127:
                    col_byte += 1 << (8 - y%8 - 1)
                if (y+1) % 8 == 0:
                    bitmap.append(col_byte)
                    col_byte = 0x00
        return bitmap

    def bitmap_to_image(self, bitmap):
        # Convert a bitmap in the format used for serial communication to an image. This is needed as an intermediate step when using the server system
        width = round(len(bitmap)/2)
        height = self.controller.height
        img = Image.new('L', (width, height), 'black')
        pixels = img.load()
        for index, col_byte in enumerate(bitmap):
            x = int(index/2)
            for byte_pos in range(8):
                y = byte_pos + 8*(index%2)
                pixels[x, y] = 255 * (col_byte & (1 << (7-byte_pos)))
        return img

    def get_bitmap(self):
        return self.image_to_bitmap(self.img)

    def init_image(self):
        self.img = Image.new('L', (self.controller.width, self.controller.height), 'black')
        self.draw = ImageDraw.Draw(self.img)
        self.draw.fontmode = "1"

    def commit(self):
        self.controller.send_bitmap(self.get_bitmap())
        self.init_image()

    def text(self, text, font = None, size = 20, halign = None, valign = None, x = None, y = None, angle = 0, color = 'white', timestring = False):
        halign = halign or 'center'
        valign = valign or 'middle'
        font = font or self.DEFAULT_FONT
        if timestring:
            text = time.strftime(text)

        textfont, truetype = self.get_imagefont(font, size)
        approx_tsize = textfont.getsize(text)
        text_img = Image.new('RGBA', approx_tsize, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.fontmode = "1"
        text_draw.text((0, 0), text, color, font = textfont)
        if truetype:
            # font.getsize is inaccurate on non-pixel fonts
            text_img = text_img.crop(text_img.getbbox())
            twidth, theight = text_img.size
        else:
            twidth, theight = approx_tsize

        if x is not None:
            textx = x
        else:
            if halign == 'center':
                textx = int((self.controller.width - twidth) / 2)
            elif halign == 'right':
                textx = int(self.controller.width - twidth)
            else:
                textx = 0
        if y is not None:
            texty = y
        else:
            if valign == 'middle':
                texty = int((self.controller.height - theight) / 2)
            elif valign == 'bottom':
                texty = int(self.controller.height - theight)
            else:
                texty = 0

        if angle:
            text_img = text_img.rotate(angle, expand = True)

        self.img.paste(text_img, (textx, texty), text_img)

    def vertical_text(self, text, font = None, size = 20, halign = None, valign = None, char_align = 'center', x = None, y = None, spacing = 2, angle = 0, color = 'white', timestring = False):
        halign = halign or 'center'
        valign = valign or 'middle'
        font = font or self.DEFAULT_FONT
        if timestring:
            text = time.strftime(text)

        textfont, truetype = self.get_imagefont(font, size)
        char_imgs = []
        for char in text:
            approx_csize = textfont.getsize(char)
            # Generate separate image for char (so size can be accurately determined, as opposed to font.getsize)
            char_img = Image.new('RGBA', approx_csize, (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.fontmode = "1"
            char_draw.text((0, 0), char, color, font = textfont)
            char_img = char_img.rotate(90, expand = True)
            char_img = char_img.crop(char_img.getbbox())
            char_imgs.append(char_img)

        # Width and height are treated looking at the non-rotated matrix from here on        
        twidth, theight = 0, 0
        # Add the spacing to text width
        twidth += spacing * len(char_imgs) - 1
        for char_img in char_imgs:
            cwidth, cheight = char_img.size
            # Text width is the width of the widest char, text height is the sum of char heights plus spacing
            if cheight > theight:
                theight = cheight
            twidth += cwidth

        text_img = Image.new('RGBA', (twidth, theight), (0, 0, 0, 0))
        xpos = 0
        for i, char_img in enumerate(char_imgs):
            cwidth, cheight = char_img.size

            if char_align == 'center':
                ypos = int((theight - cheight) / 2)
            elif char_align == 'right':
                ypos = 0
            else:
                ypos = theight - cheight

            text_img.paste(char_img, (xpos, ypos), char_img)
            xpos += cwidth + spacing

        if x is not None:
            textx = x
        else:
            if halign == 'center':
                textx = int((self.controller.width - twidth) / 2)
            elif halign == 'right':
                textx = int(self.controller.width - twidth)
            else:
                textx = 0
        if y is not None:
            texty = y
        else:
            if valign == 'middle':
                texty = int((self.controller.height - theight) / 2)
            elif valign == 'bottom':
                texty = int(self.controller.height - theight)
            else:
                texty = 0

        if angle:
            text_img = text_img.rotate(angle, expand = True)

        self.img.paste(text_img, (textx, texty), text_img)

    def bitmap(self, image, halign = None, valign = None, x = None, y = None, angle = 0):
        halign = halign or 'center'
        valign = valign or 'middle'
        if isinstance(image, Image.Image):
            img = image
        else:
            img = Image.open(image).convert('RGBA')

        if angle:
            img = img.rotate(angle, expand = True)

        bwidth, bheight = img.size

        if x is not None:
            bitmapx = x
        else:
            if halign == 'center':
                bitmapx = int((self.controller.width - bwidth) / 2)
            elif halign == 'right':
                bitmapx = int(self.controller.width - bwidth)
            else:
                bitmapx = 0
        if y is not None:
            bitmapy = y
        else:
            if valign == 'middle':
                bitmapy = int((self.controller.height - bheight) / 2)
            elif valign == 'bottom':
                bitmapy = int(self.controller.height - bheight)
            else:
                bitmapy = 0

        self.img.paste(img, (bitmapx, bitmapy), img)

    def line(self, points, color = 'white', width = 1):
        self.draw.line(points, fill = color, width = width)

    def rectangle(self, points, color = 'white', fill = False):
        self.draw.rectangle(points, fill = color if fill else None, outline = color)

    def binary_clock(self, block_width = 3, block_height = 3, block_spacing_x = 1, block_spacing_y = 1, **kwargs):
        width = 6*block_width + 5*block_spacing_x
        height = 2*block_height + block_spacing_y
        img = Image.new('RGBA', (width, height), 'black')
        draw = ImageDraw.Draw(img)
        now = datetime.datetime.now()
        hour_bits = [now.hour >> i & 1 for i in range(7, -1, -1)][-6:]
        minute_bits = [now.minute >> i & 1 for i in range(7, -1, -1)][-6:]
        
        y = 0
        for pos, bit in enumerate(hour_bits):
            x = pos * (block_width + block_spacing_x)
            draw.rectangle((x, y, x + block_width-1, y + block_height-1), outline = 'white', fill = 'white' if bit else 'black')

        y = block_height + block_spacing_y
        for pos, bit in enumerate(minute_bits):
            x = pos * (block_width + block_spacing_x)
            draw.rectangle((x, y, x + block_width-1, y + block_height-1), outline = 'white', fill = 'white' if bit else 'black')

        self.bitmap(img, **kwargs)

    def analog_clock(self, width = 16, height = 16, **kwargs):
        def rect(r, theta):
            x = r * math.cos(math.radians(theta))
            y = r * math.sin(math.radians(theta))
            return int(round(x)), int(round(y))

        def ellipse_radius(a, b, angle):
            # a: horizontal radius; b: vertical radius; angle: Angle measured from the horizontal axis
            return (a*b) / math.sqrt(a**2 * math.sin(angle)**2 + b**2 * math.cos(angle)**2)

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        now = datetime.datetime.now()
        draw.rectangle((0, 0, width-1, height-1), outline = 'white')
        center = (width/2, height/2)

        hour_angle = (now.hour % 12) * 360/12 + now.minute * 360/(12*60) - 90
        hour_length = ellipse_radius(width/2, height/2, hour_angle) * 0.3
        hour_hand = rect(hour_length, hour_angle)
        draw.line((center, (hour_hand[0]+center[0], hour_hand[1]+center[1])), fill = 'white')

        minute_angle = now.minute * 360/60 - 90
        minute_length = ellipse_radius(width/2, height/2, minute_angle) * 0.8
        minute_hand = rect(minute_length, minute_angle)
        draw.line((center, (minute_hand[0]+center[0], minute_hand[1]+center[1])), fill = 'white')

        self.bitmap(img, **kwargs)

    def black(self):
        img = Image.new('RGBA', (self.controller.width, self.controller.height), (0, 0, 0, 0))
        self.bitmap(img)

    def yellow(self):
        img = Image.new('RGBA', (self.controller.width, self.controller.height), (255, 255, 255, 255))
        self.bitmap(img)