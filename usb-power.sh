#!/bin/sh
# https://raspberrypi.stackexchange.com/questions/49440/power-usb-device-over-raspberry-pi-gpio-pin/49442#49442
# https://github.com/codazoda/hub-ctrl.c
exec /usr/local/bin/hub-ctrl -h 0 -P 2 -p $1
