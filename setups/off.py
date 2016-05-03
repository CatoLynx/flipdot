#!/usr/bin/env python3

import flipdot

client = flipdot.FlipdotClient("localhost")

client.add_graphics_submessage('panel', 'black')
client.add_graphics_submessage('front', 'black')
client.add_graphics_submessage('side', 'black')

client.set_backlight('panel', False)
client.set_backlight('side', False)
client.set_backlight('front', False)

client.commit()
