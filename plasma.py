#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from math import pi, sin
from noise import snoise2
from rpi_ws281x import PixelStrip, Color
from time import sleep

def rainbow(p):
    q = 2 * pi * p
    return Color(
        int(128.0 + 127.0 * sin(pi + q)),
        int(128.0 + 127.0 * sin(pi + q + 2 * pi / 3)),
        int(128.0 + 127.0 * sin(pi + q + 4 * pi / 3))
    )

if __name__ == '__main__':
    parser = ArgumentParser(description='Pipe pixel colors to a LED strip')
    parser.add_argument('--brightness', default=255, type=int, help='set to 0 for darkest and 255 for brightest (default: 255)')
    parser.add_argument('--fps', default=30, type=int, help='aim for specified frames per second (default: 30)')
    parser.add_argument('--gpio', default=12, type=int, help='GPIO pin connected to the LED strip (default: 12)')
    parser.add_argument('--leds', default=128, type=int, help='how many LEDs to light up (default: 128)')
    parser.add_argument('--octaves', default=2, type=int, help='noise octaves (default: 2)')
    args = parser.parse_args()
    sys.argv = []

    strip = PixelStrip(
        args.leds,
        args.gpio,
        brightness=args.brightness,
    )

    try:
        freq = 16.0 * args.octaves
        y = 0

        strip.begin()
        while True:
            for x in range(args.leds):
                color = rainbow(snoise2(x / freq, y / freq, args.octaves))
                strip.setPixelColor(x, color)
            strip.show()

            sleep(1 / args.fps)
            y += 1
    except KeyboardInterrupt:
        print('')
    finally:
        black = Color(0, 0, 0)
        for x in range(args.leds):
            strip.setPixelColor(x, black)
        strip.show()
