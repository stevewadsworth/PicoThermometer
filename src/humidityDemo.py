import gc

import machine
import utime

import sys
sys.path.append('/src')
import machine
from AHTx0 import *
from scan_i2c import *

sda = machine.Pin(4)
scl = machine.Pin(5)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
sensor = AHTx0(i2c)

# Pico Display boilerplate
import picodisplay as display
width = display.get_width()
height = display.get_height()
gc.collect()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)

bar_width = 5

# Set the display backlight to 50%
display.set_backlight(0.5)

humidities = []


while True:
    # fills the screen with black
    display.set_pen(0, 0, 0)
    display.clear()

    humidity = sensor.relative_humidity

    humidities.append(humidity)

    # shifts the temperatures history to the left by one sample
    if len(humidities) > width // bar_width:
        humidities.pop(0)

    i = 0
    for t in humidities:
        # chooses a pen colour
        display.set_pen(0, 0, 255)

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, round((height / 100) * round(100 - t)), bar_width, height)

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # draws a white background for the text
    display.set_pen(255, 255, 255)
    display.rectangle(1, 1, 100, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(0, 0, 0)
    display.text("{:.2f}".format(humidity) + "%", 3, 3, 0, 3)

    # time to update the display
    display.update()

    # waits for 5 seconds
    utime.sleep(5)
