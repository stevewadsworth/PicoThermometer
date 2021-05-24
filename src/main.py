# main.py
import sys
sys.path.append('/src')
import gc

import utime

import machine
from AHTx0 import *
from scan_i2c import *

sda = machine.Pin(4)
scl = machine.Pin(5)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
scan_bus(i2c)

sensor = AHTx0(i2c)

# Pico Display boilerplate
import picodisplay as display
width = display.get_width()
height = display.get_height()
gc.collect()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)

bar_width = 5
temp_min = 10
temp_max = 30

# Set the display backlight to 50%
display.set_backlight(0.5)

humidities = []
temperatures = []

def displayText(temperatures, humidities):
    # fills the screen with black
    display.set_pen(0, 0, 0)
    display.clear()

    display.set_pen(255, 255, 255)
    display.text("{:.2f}".format(temperatures[-1]) + "c", 10, 10, 0, 6)
    display.text("{:.2f}".format(humidities[-1]) + "%", 10, (height // 2) + 10 , 0, 6)

colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]

def temperature_to_color(temp):
    temp = min(temp, temp_max)
    temp = max(temp, temp_min)

    f_index = float(temp - temp_min) / float(temp_max - temp_min)
    f_index *= len(colors) - 1
    index = int(f_index)

    if index == len(colors) - 1:
        return colors[index]

    blend_b = f_index - index
    blend_a = 1.0 - blend_b

    a = colors[index]
    b = colors[index + 1]

    return [int((a[i] * blend_a) + (b[i] * blend_b)) for i in range(3)]

def displayTemp(temperatures, humidities):
    i = 0
    for t in temperatures:
        # chooses a pen colour based on the temperature
        display.set_pen(*temperature_to_color(t))

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, height - (round(t) * 4), bar_width, height)

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # draws a white background for the text
    display.set_pen(255, 255, 255)
    display.rectangle(1, 1, 100, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(0, 0, 0)
    display.text("{:.2f}".format(temperatures[-1]) + "c", 3, 3, 0, 3)

def displayHumidity(temperatures, humidities):
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
    display.text("{:.2f}".format(humidities[-1]) + "%", 3, 3, 0, 3)


while True:
    humidities.append(sensor.relative_humidity)
    temperatures.append(sensor.temperature)

    # shifts the history to the left by one sample
    if len(humidities) > width // bar_width:
        humidities.pop(0)

    if len(temperatures) > width // bar_width:
        temperatures.pop(0)

    #displayTemp(temperatures, humidities)
    #displayText(temperatures, humidities)
    displayHumidity(temperatures, humidities)

    # time to update the display
    display.update()

    # waits for 5 seconds
    utime.sleep(5)
