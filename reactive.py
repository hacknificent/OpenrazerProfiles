#!/usr/bin/python
import struct
import time
from threading import Thread, Lock
from openrazer.client import DeviceManager

# from openrazer.client import constants as razer_constants

# Copy this file to /usr/bin as root
# Change permissions of this file to 754
# This file in /usr/bin should be owned by root, group is root

infile_path = "/dev/input/by-path/pci-0000:00:14.0-usb-0:8:1.1-event-kbd"  # Keyboard events

COLOR = [255, 42, 187]  # RGB Color
TIMEOUT = 5  # in seconds

mutex = Lock()
countdown = TIMEOUT

# Create a DeviceManager. This is used to get specific devices
device_manager = DeviceManager()

print("Found {} Razer devices".format(len(device_manager.devices)))
print()

# Disable daemon effect syncing.
# Without this, the daemon will try to set the lighting effect to every device.
device_manager.sync_effects = False

# Iterate over each device and set the wave effect
for device in device_manager.devices:
    print("Setting {}".format(device.name))


def nif_backlight(value):
    if value > 0:
        device.fx.static(COLOR[0], COLOR[1], COLOR[2])
    else:
        device.fx.none()


def countdown_thread():
    global countdown
    while True:
        time.sleep(1)  # sleep for 1 second
        mutex.acquire()
        try:
            if countdown > 0:
                countdown -= 1
                if countdown == 0:
                    nif_backlight(0)  # turn off keyboard backlight
        finally:
            mutex.release()


nif_backlight(1)  # turn on keyboard backlight
t = Thread(target=countdown_thread)
t.start()

FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)  # are there any keyboard events?

while event:
    mutex.acquire()
    try:
        if countdown < 2:
            nif_backlight(1)  # turn on keyboard backlight
        countdown = TIMEOUT
    finally:
        mutex.release()
    event = in_file.read(EVENT_SIZE)  # are there any keyboard events?

in_file.close()
