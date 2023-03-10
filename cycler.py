#!/usr/bin/env python3
import RPi.GPIO as GPIO
import re
import subprocess
from argparse import ArgumentParser
from time import monotonic

# install cycler.service & add to crontab:
# 0 6 * * * /home/pi/LED-toys/cycler.py
# 0 22 * * * /home/pi/LED-toys/cycler.py --stop

COMMAND = ['sudo', 'systemctl']
FX = ['', 'plasma', 'pianolizer']

def list_services():
    services_command = subprocess.run([*COMMAND, '--type=service', '--state=running'], capture_output=True)
    services_output = services_command.stdout.decode('utf-8')
    all_services = re.findall(r'(\S+)\.service', services_output, re.MULTILINE)
    return [s for s in all_services if s in FX]

def stop_services(services):
    for service in services:
        subprocess.run([*COMMAND, 'stop', service])

def cycle():
    known_services = list_services()

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
        stop_services(known_services)

if __name__ == '__main__':
    parser = ArgumentParser(description='Cycle LED effects')
    parser.add_argument('--gpio', default=0, type=int, help='GPIO pin connected to the button (default: just cycle)')
    parser.add_argument('--timeout', default=60000, type=int, help='button timeout (default: 60000 ms)')
    parser.add_argument('--stop', action='store_true', help='stop all known effects')
    parser.add_argument('--sensitivity', default=0.1, type=float, help='min period between repeated button actions (default: 0.1 s)')
    parser.add_argument('--poweroff_repeat', default=3, type=int, help='press N times in row to power off (default: 3 s)')
    parser.add_argument('--poweroff_sensitivity', default=0.75, type=float, help='what counts as repeated press (default: 0.75 s)')
    args = parser.parse_args()

    if args.gpio == 0:
        if (args.stop):
            stop_services(list_services())
        else:
            cycle()
    else:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(args.gpio, GPIO.IN)

        last_action = 0
        sequence = 0
        while True:
            channel = GPIO.wait_for_edge(args.gpio, GPIO.FALLING, timeout=args.timeout)
            if not channel is None:
                now = monotonic()
                delta = now - last_action
                if delta >= args.sensitivity:
                    last_action = now
                    if delta >= args.poweroff_sensitivity:
                        sequence = 0
                        cycle()
                    else:
                        sequence += 1
                        if sequence >= args.poweroff_repeat:
                            subprocess.run(['sudo', 'poweroff'])
