bar_width = 5
temp_min = 10
temp_max = 30

def show(display, temperatures, humidities):
    i = 0
    for t in humidities:
        # chooses a pen colour
        display.set_pen(0, 0, 255)

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, round((display.get_height() / 100) * round(100 - t)), bar_width, display.get_height())

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # draws a white background for the text
    display.set_pen(255, 255, 255)
    display.rectangle(1, 1, 100, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(0, 0, 0)
    display.text("{:.2f}".format(humidities[-1]) + "%", 3, 3, 0, 3)
