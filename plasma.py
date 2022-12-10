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
    brightness = 32
    width = 128

    height = 1024
    octaves = 4
    freq = 16.0 * octaves

    frames = []
    for y in range(height):
        line = [rainbow(snoise2(x / freq, y / freq, octaves)) for x in range(width)]
        frames.append(line)
    frames += list(reversed(frames))

    strip = PixelStrip(
        width,
        gpio,
        brightness=brightness,
    )
    strip.begin()

    i = 0
    while True:
        frame = frames[i % len(frames)]
        i += 1

        for x in range(width):
            strip.setPixelColor(x, frame[x])
        strip.show()

        sleep(1 / fps)
