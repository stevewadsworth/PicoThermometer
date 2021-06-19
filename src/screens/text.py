from Results import Results

def show(display, temperature_results:Results, humidity_results:Results):
    display.set_pen(255, 255, 255)
    display.text("{:.2f}".format(temperature_results.latest) + "c", 10, 10, 0, 6)
    display.text("{:.2f}".format(humidity_results.latest) + "%", 10, (display.get_height() // 2) + 10 , 0, 6)
