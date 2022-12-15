#!/usr/bin/env python3
from rpi_ws281x import PixelStrip, Color
from time import sleep

LEDS = 288
GPIO = 12
BRIGHTNESS = 255
DELAY = 0.01

if __name__ == '__main__':
    strip = PixelStrip(
        LEDS,
        GPIO,
        brightness=BRIGHTNESS,
    )
    strip.begin()

    for y in range(0, 255, 32):
        color = Color(y, 0, 0)
        for x in range(LEDS):
            strip.setPixelColor(x, color)
            strip.show()
            sleep(DELAY)
