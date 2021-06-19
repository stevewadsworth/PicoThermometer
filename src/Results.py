import micropython
from machine import Timer

class Results:
    def __init__(self, sensor, max_results=100, update_rate=6000):
        self.__sensor = sensor
        self.__bound_update = self.__update
        self.__values = []
        self.__max_results = max_results
        # Got to add the first reading straight away or anybody that tries to read it will get an error
        self.__update(self.__sensor())
        Timer(mode=Timer.PERIODIC, period=update_rate, callback=self.__read_sensor)

    def __update(self, value):
        self.__values.append(value)
        if len(self.__values) > self.__max_results:
            self.__values.pop(0)

    def __read_sensor(self, tim):
        micropython.schedule(self.__bound_update, self.__sensor())

    @property
    def values(self):
        return self.__values

    @property
    def latest(self):
        return self.__values[-1]
