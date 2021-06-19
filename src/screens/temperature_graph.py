bar_width = 5
temp_min = 10
temp_max = 30

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

def show(display, temperatures, humidities):
    i = 0
    for t in temperatures:
        # chooses a pen colour based on the temperature
        display.set_pen(*temperature_to_color(t))

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, display.get_height() - (round(t) * 4), bar_width, display.get_height())

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # draws a white background for the text
    display.set_pen(255, 255, 255)
    display.rectangle(1, 1, 100, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(0, 0, 0)
    display.text("{:.2f}".format(temperatures[-1]) + "c", 3, 3, 0, 3)
