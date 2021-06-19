# main.py
import sys
import gc

import utime

from machine import Pin
from machine import I2C

sys.path.append('/src')

from AHTx0 import AHTx0
from Button import Button
import screens.text as text
import screens.humidity_graph as humidity_graph
import screens.temperature_graph as temperature_graph

from Results import Results

# Pico Display boilerplate
import picodisplay as display
gc.collect()
display_buffer = bytearray(display.get_width() * display.get_height() * 2)
display.init(display_buffer)

# Set the display backlight to 50%
display.set_backlight(0.5)

bar_width = 5

SCREEN_REFRESH_SECONDS = 5
BUTTON_SCAN_SECONDS = 0.1

layout_to_use = 0

# Define the buttons on the pico display
button_A = Button(Pin(12, Pin.IN, Pin.PULL_UP))
button_B = Button(Pin(13, Pin.IN, Pin.PULL_UP))
button_X = Button(Pin(14, Pin.IN, Pin.PULL_UP))
button_Y = Button(Pin(15, Pin.IN, Pin.PULL_UP))

def button_next(x):
    global layout_to_use
    layout_to_use += 1
    if layout_to_use >= len(layouts):
        layout_to_use = 0

def button_prev(x):
    global layout_to_use
    layout_to_use -= 1
    if layout_to_use < 0:
        layout_to_use = len(layouts) - 1

button_A.on_press(button_next)
button_B.on_press(button_prev)

sda = Pin(4)
scl = Pin(5)
i2c = I2C(0, sda=sda, scl=scl, freq=400000)

sensor = AHTx0(i2c)

humidities = Results(max_results=display.get_width() // bar_width, sensor=lambda : sensor.relative_humidity)
temperatures = Results(max_results=display.get_width() // bar_width, sensor=lambda : sensor.temperature)

layouts = [
    text,
    temperature_graph,
    humidity_graph
]

while True:
    for i in range(0, SCREEN_REFRESH_SECONDS // BUTTON_SCAN_SECONDS):

        # fills the screen with black
        display.set_pen(0, 0, 0)
        display.clear()

        layouts[layout_to_use].show(display, temperatures, humidities)

        # time to update the display
        display.update()

        utime.sleep(BUTTON_SCAN_SECONDS)
