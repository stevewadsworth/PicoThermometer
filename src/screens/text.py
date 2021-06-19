def show(display, temperatures, humidities):
    display.set_pen(255, 255, 255)
    display.text("{:.2f}".format(temperatures[-1]) + "c", 10, 10, 0, 6)
    display.text("{:.2f}".format(humidities[-1]) + "%", 10, (display.get_height() // 2) + 10 , 0, 6)
