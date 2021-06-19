import micropython
from machine import Pin, Timer

# Make sure we can handle exceptions in the ISR
micropython.alloc_emergency_exception_buf(100)

class Button:
    # Define the possible button events
    RELEASE = 0
    PRESS = 1
    LONG_PRESS = 2

    def __init__(self, pin: Pin, active_high=False, long_press_duration=500):
        self.__long_press_duration = long_press_duration
        # Initialise the callbacks to 'None'
        self.__pressed_fn = None
        self.__long_pressed_fn = None
        self.__released_fn = None
        self.__event_fn = None
        # Create the long press timer
        self.__tim = Timer()
        # Is this active high or active low button?
        self.__active_value = 1 if active_high else 0
        # Very simple debounce logic
        if pin.value() == self.__active_value:
            self.__is_pressed = True
        else:
            self.__is_pressed = False
        # Setup the interrupt
        pin.irq(self._button_pressed, Pin.IRQ_FALLING | Pin.IRQ_RISING)

    @property
    def is_pressed(self):
        return self.__is_pressed

    def on_press(self, cb):
        self.__pressed_fn = cb
        return self

    def on_long_press(self, cb):
        self.__long_pressed_fn = cb
        return self

    def on_release(self, cb):
        self.__released_fn = cb
        return self

    def on_event(self, cb):
        self.__event_fn = cb
        return self

    def _notify(self, event):
        if self.__event_fn:
            micropython.schedule(self.__event_fn, event)

        if event == Button.RELEASE:
            if self.__released_fn:
                micropython.schedule(self.__released_fn, Button.RELEASE)
        elif event == Button.PRESS:
            if self.__pressed_fn:
                micropython.schedule(self.__pressed_fn, Button.PRESS)
        elif event == Button.LONG_PRESS:
            if self.__long_pressed_fn:
                micropython.schedule(self.__long_pressed_fn, Button.LONG_PRESS)

    def _long_press(self, tim):
        tim.deinit()
        # A long press has been detected
        self._notify(Button.LONG_PRESS)

    def _button_pressed(self, pin):
        if pin.value() == self.__active_value and not self.__is_pressed:
            # The button has been pressed
            self.__tim.init(mode=Timer.ONE_SHOT, period=self.__long_press_duration, callback=self._long_press)
            self.__is_pressed = True
            self._notify(Button.PRESS)
        elif pin.value() != self.__active_value and self.__is_pressed:
            # The button has been released
            self.__tim.deinit()
            self.__is_pressed = False
            self._notify(Button.RELEASE)
