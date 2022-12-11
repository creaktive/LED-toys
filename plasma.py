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

# https://github.com/ArashPartow/bitmap/blob/master/bitmap_image.hpp#L2859
def convert_wave_length_nm_to_rgb(wave_length_nm, gamma=0.8):
    # Credits: Dan Bruton http://www.physics.sfasu.edu/astro/color.html
    red = 0.0
    green = 0.0
    blue = 0.0
    if wave_length_nm >= 380.0 and wave_length_nm < 440.0:
        red = -(wave_length_nm - 440.0) / (440.0 - 380.0)
        blue = 1.0
    elif wave_length_nm >= 440.0 and wave_length_nm < 490.0:
        green = (wave_length_nm - 440.0) / (490.0 - 440.0)
        blue = 1.0
    elif wave_length_nm >= 490.0 and wave_length_nm < 510.0:
        green = 1.0
        blue = -(wave_length_nm - 510.0) / (510.0 - 490.0)
    elif wave_length_nm >= 510.0 and wave_length_nm < 580.0:
        red = (wave_length_nm - 510.0) / (580.0 - 510.0)
        green = 1.0
    elif wave_length_nm >= 580.0 and wave_length_nm < 645.0:
        red = 1.0
        green = -(wave_length_nm - 645.0) / (645.0 - 580.0)
    elif wave_length_nm >= 645.0 and wave_length_nm <= 780.0:
        red = 1.0

    factor = 0.0
    if wave_length_nm >= 380.0 and wave_length_nm < 420.0:
        factor = 0.3 + 0.7 * (wave_length_nm - 380.0) / (420.0 - 380.0)
    elif wave_length_nm >= 420.0 and wave_length_nm < 701.0:
        factor = 1.0
    elif wave_length_nm >= 701.0 and wave_length_nm <= 780.0:
        factor = 0.3 + 0.7 * (780.0 - wave_length_nm) / (780.0 - 700.0)

    intensity_max = 255.0
    return Color(
        0 if red == 0.0 else int(round(intensity_max * pow(red * factor, gamma))),
        0 if green == 0.0 else int(round(intensity_max * pow(green * factor, gamma))),
        0 if blue == 0.0 else int(round(intensity_max * pow(blue * factor, gamma)))
    )

def clamp(x, minimum=0.0, maximum=1.0):
    return max(minimum, min(x, maximum))

NANOSECONDS_IN_SECOND = 1_000_000_000
def sleep_ns(ns):
    return sleep(ns / NANOSECONDS_IN_SECOND)

if __name__ == '__main__':
    parser = ArgumentParser(description='Play plasma effect on a WS2812B RGB LED strip')
    parser.add_argument('--brightness', default=255, type=int, help='set to 0 for darkest and 255 for brightest (default: 255)')
    parser.add_argument('--fps', default=48, type=int, help='aim for specified frames per second (default: 48)')
    parser.add_argument('--gpio', default=12, type=int, help='GPIO pin connected to the LED strip (default: 12)')
    parser.add_argument('--leds', default=288, type=int, help='how many LEDs to light up (default: 288)')
    parser.add_argument('--octaves', default=5, type=int, help='noise octaves (default: 5)')
    parser.add_argument('--sway_amount', default=100.0, type=float, help='sway amount (default: 100.0)')
    parser.add_argument('--sway_period', default=30.0, type=float, help='sway period, in seconds (default: 30.0)')
    parser.add_argument('--gamma', default=0.8, type=float, help='gamma (default: 0.8)')
    parser.add_argument('--scroll_step', default=0.1, type=float, help='scroll step (default: 0.1)')
    args = parser.parse_args()

    strip = PixelStrip(
        args.leds,
        args.gpio,
        brightness=args.brightness,
    )

    freq = 16.0 * args.octaves
    interval = int(NANOSECONDS_IN_SECOND / args.fps)
    y = 0.0

    killer = GracefulKiller()
    strip.begin()
    while not killer.kill_now:
        next_frame = monotonic_ns() + interval

        sway = args.sway_amount * sin(2.0 * pi * y / (args.fps * args.sway_period))
        for x in range(args.leds):
            noise = clamp(0.5 + snoise2((x + sway) / freq, y / freq, args.octaves))
            color = convert_wave_length_nm_to_rgb(380.0 + 400.0 * noise, args.gamma)
            strip.setPixelColor(x, color)
        y += args.scroll_step
        strip.show()

        now = monotonic_ns()
        if next_frame > now:
            sleep_ns(next_frame - now)

    black = Color(0, 0, 0)
    for x in range(args.leds):
        strip.setPixelColor(x, black)
    strip.show()
