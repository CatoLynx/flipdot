#!/usr/bin/env python3

import flipdot

client = flipdot.FlipdotClient("localhost")

client.add_graphics_submessage('panel', 'text', text = "%d%m%y", timestring = True, font = "Itty", size = 4, y = 1, refresh_interval = 'minute')
client.add_graphics_submessage('panel', 'binary_clock', block_spacing_x = 2, y = 7, refresh_interval = 'minute')

client.add_graphics_submessage('side', 'text', text = "Deaktiviert", font = "FIS_20")

client.add_graphics_submessage('front', 'text', text = "Deaktiviert", font = "FIS_20", halign = 'right')

client.set_backlight('panel', False)
client.set_backlight('side', False)
client.set_backlight('front', False)

client.commit()