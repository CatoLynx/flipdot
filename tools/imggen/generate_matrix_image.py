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
This program can connect to a flipdot server and generate a realistic image of the selected matrix display.
"""

skeleton_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   id="svg2"
   version="1.1"
   width="{width}"
   height="{height}"
   viewBox="0 0 {width} {height}">
   <defs
     id="defs13">
    <filter
       height="1.5904703"
       y="-0.29523513"
       width="1.6098424"
       x="-0.30492119"
       id="filter4437"
       style="color-interpolation-filters:sRGB">
      <feGaussianBlur
         id="feGaussianBlur4439"
         stdDeviation="7.0254623" />
    </filter>
  </defs>
  <metadata
     id="metadata8">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <rect
     id="background"
     x="0"
     y="0"
     height="{height}"
     width="{width}"
     style="opacity: 1; fill: #{background_color};" />
     {data}
</svg>"""

pixel_xml = """  <g
     id="pixel-{row}-{col}"
     transform="translate({xpos}, {ypos})">
    <rect
       id="axis"
       x="-31.947792"
       y="38.746765"
       height="3.4"
       width="64.0"
       transform="matrix(0.70710678,-0.70710678,0.70710678,0.70710678,0,0)"
       style="opacity: 1; fill: #{axis_color};" />
    <circle
       id="peg-inactive"
       cx="-8.8"
       cy="8.8"
       r="5.0"
       transform="matrix(0,-1,1,0,0,0)"
       style="opacity: 1; fill: #{inactive_peg_color};" />
    <path
       id="flipdot-active"
       d="M 50.7,16.3 C 46,11.5 41.3,6.6 36.6,1.8 c -6.7,0 -13.3,0 -20,0 -4.7,4.8 -9.4,9.6 -14.1,14.5 0,6.8 0,13.6 0,20.5 4.7,4.8 9.4,9.7 14.1,14.5 6.7,0 13.3,0 20,0 0.7,-0.7 1.4,-1.4 2.1,-2.2 -1.1,-5.7 4.3,-11.4 10.1,-10.6 0.8,-0.1 1.3,-1.2 1.9,-1.7 0,-6.8 0,-13.6 0,-20.5 z"
       style="opacity: {active}; fill: #{active_color};" />
    <path
       id="light"
       d="M 57.422607,-57.198761 A 28.555391,55.296612 0 0 1 43.144911,-9.31049 28.555391,55.296612 0 0 1 14.58952,-9.3104913 28.555391,55.296612 0 0 1 0.3118248,-57.198764 l 28.5553912,3e-6 z"
       transform="matrix(0,0.63493711,-0.80921481,0,8.2860939,13.716316)"
       style="opacity: {light}; fill: #{light_color}; filter: url(#filter4437);" />
    <circle
       id="peg-active"
       cx="-48.3"
       cy="48.3"
       r="5.0"
       transform="matrix(0,-1,1,0,0,0)"
       style="opacity: 1; fill: #{active_peg_color};" />
    <path
       id="flipdot-inactive"
       d="m 6.5,40.9 c 4.7,4.8 9.4,9.7 14.1,14.5 6.7,0 13.3,0 20,0 4.7,-4.8 9.4,-9.6 14.1,-14.5 0,-6.8 0,-13.6 0,-20.5 C 50,15.6 45.3,10.7 40.6,5.9 c -6.7,0 -13.3,0 -20,0 -0.7,0.7 -1.4,1.4 -2.1,2.2 1.1,5.7 -4.3,11.4 -10.1,10.6 -0.8,0.1 -1.3,1.2 -1.9,1.7 0,6.8 0,13.6 0,20.5 z"
       style="opacity: {inactive}; fill: #{inactive_color};" />
    <circle
       id="peg-active"
       cx="-48.3"
       cy="48.3"
       r="5.0"
       transform="matrix(0,-1,1,0,0,0)"
       style="opacity: 1; fill: #{active_peg_color};" />
    <path
       id="support-bottom-right"
       d="M 57.2,14.7 42.5,0 57.2,0 Z"
       style="opacity: 1; fill: #{support_color};" />
    <path
       id="support-top-left"
       d="M 0,42.5 14.7,57.2 0,57.2 Z"
       style="opacity: 1; fill: #{support_color};" />
  </g>"""

import argparse
import flipdot
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type = str, required = False, default = "localhost")
    parser.add_argument('-p', '--port', type = int, required = False, default = 1820)
    parser.add_argument('-d', '--display', type = str, required = True)
    parser.add_argument('-o', '--output-file', type = str, required = True)
    parser.add_argument('-png', '--png', action = 'store_true')
    args = parser.parse_args()

    client = flipdot.FlipdotClient(args.server, args.port)
    hwconfig = client.get_hwconfig()
    display = hwconfig[args.display]
    config = client.get_config([args.display])[args.display]
    bitmap = client.get_bitmap([args.display])[args.display]

    backlight = config['backlight']

    data = ""
    for row in range(display['height']):
        for col in range(display['width']):
            pixel_active = bool(bitmap[col*2 + int(row/8)] & (128 >> row%8))
            pixel_data = {
                'row': row,
                'col': col,
                'xpos': col * 57.2,
                'ypos': row * 57.2,
                'inactive': int(not pixel_active),
                'active': int(pixel_active),
                'inactive_color': "222",
                'active_color': "bb0",
                'support_color': "222",
                'axis_color': "000",
                'inactive_peg_color': "222",
                'active_peg_color': "222",
                'light_color': "ef0",
                'light': int(pixel_active and backlight)
            }

            data += pixel_xml.format(**pixel_data)

    with open(args.output_file, 'w') as f:
        f.write(skeleton_xml.format(**{
            'data': data,
            'width': display['width'] * 57.2,
            'height': display['height'] * 57.2,
            'background_color': "00000000"
        }))

    if args.png:
        subprocess.call(("rsvg-convert", args.output_file, "-o", args.output_file + ".png"))

if __name__ == "__main__":
    main()