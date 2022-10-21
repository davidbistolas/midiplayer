from time import ticks_us

from machine import Pin


class SimpleButton:
    """
    Hardware Button, with debounce
    """

    def __init__(self, pin, callback=None, bounce_time=45):
        self.button = pin
        self.callback = callback
        self.button.irq(trigger=Pin.IRQ_RISING, handler=self.on_press, )
        self._debounce_time = bounce_time * 10000.0
        self._last_press = 0.0

    def on_press(self, event):
        if self.debounce():
            self.callback()

    def debounce(self):
        if ticks_us() - self._last_press > self._debounce_time:
            self._last_press = ticks_us()
            return True
        else:
            return False
