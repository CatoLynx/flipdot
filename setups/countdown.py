#!/usr/bin/env python3

import argparse
import datetime
import flipdot
import time

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--display', type = str, required = True)
parser.add_argument('-m', '--minutes', type = int, required = True)
args = parser.parse_args()

client = flipdot.FlipdotClient("localhost")

target = datetime.datetime.now() + datetime.timedelta(minutes = args.minutes)

while datetime.datetime.now() < target:
    seconds = (target-datetime.datetime.now()).total_seconds()
    minutes, seconds = divmod(seconds, 60)
    client.add_graphics_submessage(args.display, 'text', text = "%04i" % (minutes+1), font = "FIS_20")
    client.commit()
    time.sleep(60)

client.add_graphics_submessage(args.display, 'text', text = "END", font = "Luminator7_Bold")
client.commit()