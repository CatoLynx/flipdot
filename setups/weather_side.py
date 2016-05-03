#!/usr/bin/env python3

import flipdot
import pyowm
import re
import requests
import time
import traceback

from lxml import html
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

# Get weather alerts
plz = 63571
page = requests.get("http://www.unwetterzentrale.de/uwz/getwarning_de.php?plz={plz}&uwz=UWZ-DE&lang=de".format(plz = plz))
page.encoding = 'UTF-8'
tree = html.fromstring(page.content)
divs = tree.xpath('//*[@id="content"]/div')
warnings = []
for div in divs:
    # Only process divs that contain warnings
    warning = div.xpath('div[1]/div[1]/div[1]')
    if not warning:
        continue
    match = re.match(r"Unwetterwarnung Stufe (?P<level>\w+) vor (?P<what>\w+)", warning[0].text)
    if not match:
        continue
    data = match.groupdict()
    warnings.append(data)

if warnings:
    client.set_inverting('side', True)
    client.add_graphics_submessage('side', 'text', text = warnings[0]['what'].upper(), font = "Luminator7_Bold", halign = 'center', y = 1)
    client.add_graphics_submessage('side', 'text', text = warnings[0]['level'].upper(), font = "Luminator5_Bold", halign = 'center', y = 10)
else:
    # Get weather
    owm = pyowm.OWM(API_KEY, language = 'de')
    obs = owm.weather_at_id(2872493)
    w = obs.get_weather()
    icon = w.get_weather_icon_name()
    temp = w.get_temperature('celsius')['temp']
    status = _prepare_status(w.get_detailed_status())
    humidity = w.get_humidity()
    wind = w.get_wind()['speed'] * 3.6 # Speed is in m/sec

    client.set_inverting('side', False)
    client.add_graphics_submessage('side', 'bitmap', image = "bitmaps/weather_icons/{0}.png".format(icon), x = 0, y = 0)
    client.add_graphics_submessage('side', 'text', text = status, font = "Flipdot8_Narrow", x = 18, y = 0)
    client.add_graphics_submessage('side', 'text', text = "{0:.1f}°C {1}% {2:.0f}km/h".format(temp, humidity, wind), font = "Flipdot8_Narrow", x = 18, y = 9)

client.commit()