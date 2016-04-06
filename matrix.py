#!/usr/bin/env python3

import argparse
import datetime
import flipdot
import time

from PIL import Image, ImageSequence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type = str, choices = ('clock', 'vclock', 'smallclock', 'mediumclock'), required = False)
    parser.add_argument('-p', '--port', type = str, required = True)
    parser.add_argument('-w', '--width', type = int, default = 28, required = False)
    parser.add_argument('-t', '--text', type = str, required = False)
    parser.add_argument('-vt', '--vertical-text', type = str, required = False)
    parser.add_argument('-s', '--size', type = int, default = 16, required = False)
    parser.add_argument('-f', '--font', type = str, default = "Arial Bold", required = False)
    parser.add_argument('-ha', '--horizontal-align', type = str, choices = ('left', 'center', 'right'), default = 'center', required = False)
    parser.add_argument('-va', '--vertical-align', type = str, choices = ('top', 'middle', 'bottom'), default = 'middle', required = False)
    parser.add_argument('-b', '--backlight', type = str, choices = ('on', 'off'), required = False)
    parser.add_argument('-i', '--image', type = argparse.FileType('rb'), required = False)
    parser.add_argument('-l', '--loop', action = 'store_true')
    parser.add_argument('-d', '--delay', type = float, default = 0.0, required = False)
    args = parser.parse_args()

    matrix = flipdot.FlipdotController(args.port, args.width)
    graphics = flipdot.FlipdotGraphics(matrix)

    if args.backlight == 'on':
        matrix.set_backlight(True)
    elif args.backlight == 'off':
        matrix.set_backlight(False)

    if args.action == 'clock':
        old_minute = None
        while True:
            now = datetime.datetime.now()
            if now.minute != old_minute:
                graphics.text(now.strftime("%H:%M"), size = 22, x = 44)
                #graphics.text(now.strftime("%d.%m.%y"), align = 'left', valign = 'top', size = 4, font = "fonts/itty.ttf")
                #graphics.bitmap(graphics.img_binary_clock(block_width = 4, block_height = 4), align = 'left', valign = 'bottom')
                graphics.bitmap(graphics.img_analog_clock(), align = 'right', valign = 'middle')
                graphics.commit()
            old_minute = now.minute
            time.sleep(1)
    elif args.action == 'smallclock':
        old_minute = None
        while True:
            now = datetime.datetime.now()
            if now.minute != old_minute:
                graphics.add_text(now.strftime("%H:%M"), size = 14, font = "Arial Narrow Bold")
                graphics.commit()
            old_minute = now.minute
            time.sleep(1)
    elif args.action == 'mediumclock':
        old_minute = None
        while True:
            now = datetime.datetime.now()
            if now.minute != old_minute:
                graphics.text(now.strftime("%H:%M"), size = 22, x = 30)
                graphics.text(now.strftime("%d.%m.%y"), align = 'left', valign = 'top', size = 4, font = "Itty")
                graphics.bitmap(graphics.img_binary_clock(block_width = 4, block_height = 4), align = 'left', valign = 'bottom')
                graphics.commit()
            old_minute = now.minute
            time.sleep(1)
    elif args.action == 'vclock':
        old_minute = None
        while True:
            now = datetime.datetime.now()
            if now.minute != old_minute:
                graphics.vertical_text(now.strftime("%H:%M"), size = 33)
                graphics.commit()
            old_minute = now.minute
            time.sleep(1)
    else:
        if args.image:
            img = Image.open(args.image)
            if img.format == 'GIF':
                while True:
                    img = Image.open(args.image)
                    for frame in ImageSequence.Iterator(img):
                        graphics.bitmap(frame)
                        graphics.commit()
                        time.sleep(args.delay)
                    if not args.loop:
                        break
                    del img # If we don't completely reload the image, the first frame will be skipped (the last one will be displayed instead) on any but the first cycles
            else:
                graphics.bitmap(img)
                graphics.commit()
        elif args.text:
            graphics.text(args.text, args.font, args.size, args.horizontal_align, args.vertical_align)
            graphics.commit()
        elif args.vertical_text:
            graphics.vertical_text(args.vertical_text, args.font, args.size, args.horizontal_align, args.vertical_align)
            graphics.commit()

if __name__ == "__main__":
    main()
