#!/usr/bin/env python3
import signal
from argparse import ArgumentParser
from math import pi, sin
from noise import snoise2
from rpi_ws281x import PixelStrip, Color
from time import monotonic_ns, sleep

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True

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
    parser.add_argument('--leds', default=288, type=int, help='how many LEDs to light up (default: 288)')
    parser.add_argument('--octaves', default=5, type=int, help='noise octaves (default: 5)')
    args = parser.parse_args()

    strip = PixelStrip(
        args.leds,
        args.gpio,
        brightness=args.brightness,
    )

    freq = 16.0 * args.octaves
    interval = 1.0 / args.fps
    y = 0

    killer = GracefulKiller()
    strip.begin()
    timestamp = monotonic_ns()
    while not killer.kill_now:
        for x in range(args.leds):
            color = rainbow(snoise2(x / freq, y / freq, args.octaves))
            strip.setPixelColor(x, color)
        y += 1
        strip.show()

        now = monotonic_ns()
        sleep_for = interval - ((now - timestamp) / 1_000_000_000)
        timestamp = now
        if sleep_for > 0:
            sleep(sleep_for)

    black = Color(0, 0, 0)
    for x in range(args.leds):
        strip.setPixelColor(x, black)
    strip.show()
