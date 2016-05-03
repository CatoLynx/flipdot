#!/usr/bin/env python3

import datetime
import flipdot
import pyowm
import time
import traceback

from owm_apikey import API_KEY

def upperfirst(x):
    return x[0].upper() + x[1:]

def _prepare_status(status):
    replacements = {
        "Überwiegend": "überw.",
        "Leichte Regenschauer": "Leichte Regensch."
    }
    status = upperfirst(status)
    for orig, repl in replacements.items():
        status = status.replace(orig, repl)
    return status

client = flipdot.FlipdotClient("localhost")
owm = pyowm.OWM(API_KEY, language = 'de')

fc = owm.three_hours_forecast("Darmstadt").get_forecast() # Darmstadt
weathers = fc.get_weathers()
now = datetime.datetime.now()
displayed_weathers = []

for w in weathers:
    dt = datetime.datetime.fromtimestamp(w.get_reference_time())
    if now.hour < 8: # Choose today's forecast before 8:00
        if dt.day == now.day:
            if dt.hour in (8, 11, 14):
                displayed_weathers.append(w)
    else: # Choose tomorrow's forecast after 8:00
        if dt.date() == now.date() + datetime.timedelta(days = 1):
            if dt.hour in (8, 11, 14):
                displayed_weathers.append(w)

for index, w in enumerate(displayed_weathers):
    icon = w.get_weather_icon_name()
    temp = w.get_temperature('celsius')['temp']
    status = w.get_status()
    humidity = w.get_humidity()
    wind = w.get_wind()['speed'] * 3.6 # Speed is in m/sec
    xbase = 44*index
    client.add_graphics_submessage('front', 'bitmap', image = "bitmaps/weather_icons/{0}.png".format(icon), x = xbase, y = 0)
    client.add_graphics_submessage('front', 'bitmap', image = "bitmaps/weather_icons/temperature7.png", x = xbase+18, y = 0)
    client.add_graphics_submessage('front', 'bitmap', image = "bitmaps/weather_icons/wind7.png", x = xbase+18, y = 9)
    client.add_graphics_submessage('front', 'text', text = "{0:.1f}".format(temp), font = "Flipdot8_Narrow", x = xbase+25, y = 0)
    client.add_graphics_submessage('front', 'text', text = "{0:.1f}".format(wind), font = "Flipdot8_Narrow", x = xbase+25, y = 9)

client.add_graphics_submessage('front', 'line', points = [40, 0, 40, 15], width = 2)
client.add_graphics_submessage('front', 'line', points = [84, 0, 84, 15], width = 2)
client.commit()