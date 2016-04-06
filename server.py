#!/usr/bin/env python3

import flipdot

server = flipdot.FlipdotServer("/dev/ttyUSB1", 
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