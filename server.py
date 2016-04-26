#!/usr/bin/env python3

import argparse
import flipdot

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type = str, required = True)
args = parser.parse_args()

server = flipdot.FlipdotServer(args.port, 
    {
        'side': {
            'width': 84,
            'height': 16,
            'address': 0
        },
        'panel': {
            'width': 28,
            'height': 16,
            'address': 1
        },
        'front': {
            'width': 126,
            'height': 16,
            'address': 2
        }
    })
server.run()
