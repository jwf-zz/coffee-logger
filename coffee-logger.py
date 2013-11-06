#!/usr/bin/python

from settings import *
import time, json, httplib, os, atexit, thread
import RPi.GPIO as io
from evdev import InputDevice, list_devices, categorize, ecodes
from parse_rest.connection import register
from parse_rest.datatypes import Object, Function

# V+ is bottom row, third from the left.
# V- is top-leftmost pin.
POWER_PIN = 25

KEYCODES = {
	'KEY_0': '0', 'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 
	'KEY_5': '5', 'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9'
}

class CoffeeLog(Object):
    pass

def get_scanner_device():
    devices = map(InputDevice, list_devices())
    device = None
    for dev in devices:
        if dev.name == 'RFIDeas USB Keyboard':
            device = dev
            break
    return device

def init(device):
	io.setwarnings(False)
	io.setmode(io.BCM)
	io.setup(POWER_PIN, io.OUT)
	io.output(POWER_PIN, False)
	register(APPLICATION_ID, REST_API_KEY)

	atexit.register(cleanup, device)

	device.grab()

def cleanup(device):
	device.ungrab()
	io.output(POWER_PIN, False)

def log(badgenum):
	newlog = CoffeeLog(badge_num=badgenum, time=time.strftime("%Y-%m-%d %H:%M:%S"), machine="SEA0017A")
	newlog.save()

def get_input(device):
	val = ''
	for event in device.read_loop():
		ev = categorize(event)
		if event.type == ecodes.EV_KEY and ev.keystate == ev.key_down:
			if ev.keycode == 'KEY_ENTER':
				break
			val += KEYCODES[ev.keycode]
	return val

if __name__ == "__main__":
	device = get_scanner_device()
	if str(device) == 'None':
		print "Device not found! Exiting!"

	init(device)
	while True:
		try: 
			badgenum = int(get_input(device))
			io.output(POWER_PIN, True)
			thread.start_new_thread(log, (badgenum,))
			time.sleep(60)
			io.output(POWER_PIN, False)
		except ValueError:
			time.sleep(0.1)

