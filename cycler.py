#!/usr/bin/env python3
import RPi.GPIO as GPIO
import re
import subprocess
from argparse import ArgumentParser

COMMAND = ['sudo', 'systemctl']
FX = ['', 'plasma', 'pianolizer']

def cycle():
    services_command = subprocess.run([*COMMAND, '--type=service', '--state=running'], capture_output=True)
    services_output = services_command.stdout.decode('utf-8')
    all_services = re.findall(r'(\S+)\.service', services_output, re.MULTILINE)
    known_services = [s for s in all_services if s in FX]

    n = len(known_services)
    if n == 0:
        subprocess.run([*COMMAND, 'start', FX[1]])
    elif n == 1:
        idx_this = FX.index(known_services[0])
        idx_next = (idx_this + 1) % len(FX)

        subprocess.run([*COMMAND, 'stop', FX[idx_this]])
        if idx_next > 0:
            subprocess.run([*COMMAND, 'start', FX[idx_next]])
    else:
        for service in known_services:
            subprocess.run([*COMMAND, 'stop', service])

if __name__ == '__main__':
    parser = ArgumentParser(description='Cycle LED effects')
    parser.add_argument('--gpio', default=0, type=int, help='GPIO pin connected to the button (default: just cycle)')
    parser.add_argument('--timeout', default=5000, type=int, help='button timeout (default: 5000 ms)')
    args = parser.parse_args()

    if args.gpio == 0:
        cycle()
    else:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(args.gpio, GPIO.IN)

        while True:
            channel = GPIO.wait_for_edge(args.gpio, GPIO.FALLING, timeout=args.timeout)
            if not channel is None:
                cycle()
