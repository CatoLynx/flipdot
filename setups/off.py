#!/usr/bin/env python3

import flipdot

client = flipdot.FlipdotClient("localhost")

client.add_graphics_submessage('panel', 'text', text = "")
client.add_graphics_submessage('front', 'text', text = "")
client.add_graphics_submessage('side', 'text', text = "")

client.set_backlight('panel', False)
client.set_backlight('side', False)
client.set_backlight('front', False)

client.commit()