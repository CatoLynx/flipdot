#!/usr/bin/env python3

import flipdot

client = flipdot.FlipdotClient("localhost")

client.add_graphics_submessage('panel', 'text', text = "%d%m%y", timestring = True, font = "Itty", size = 4, top = 1, refresh_interval = 'minute')
client.add_graphics_submessage('panel', 'binary_clock', block_spacing_x = 2, top = 7, refresh_interval = 'minute')

client.set_backlight('panel', False)
client.set_backlight('side', False)
client.set_backlight('front', False)

client.commit()