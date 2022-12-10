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
    fps = 30
    gpio = 12
    brightness = 16
    width = 128

    octaves = 4
    freq = 16.0 * octaves

    strip = PixelStrip(
        width,
        gpio,
        brightness=brightness,
    )
    strip.begin()

    try:
        y = 0
        while True:
            for x in range(width):
                color = rainbow(snoise2(x / freq, y / freq, octaves))
                strip.setPixelColor(x, color)
            strip.show()

            sleep(1 / fps)
            y += 1
    except KeyboardInterrupt:
        print('')
    finally:
        black = Color(0, 0, 0)
        for x in range(width):
            strip.setPixelColor(x, black)
        strip.show()
