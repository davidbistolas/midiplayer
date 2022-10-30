from time import ticks_ms

from machine import Pin


class SimpleButton:
    """
    Hardware Button, with debounce
    """

    def __init__(self, pin, callback=None, bounce_time=450):
        self.button = pin
        self.callback = callback
        self.button.irq(trigger=Pin.IRQ_RISING, handler=self.on_press)
        self._debounce_time = bounce_time # * 10000.0
        self._last_press = 0.0

    def on_press(self, event):
        if self.debounce():
            self.callback()

    def debounce(self):
        # print("Debouncing ",self,"-", ticks_us(), self._last_press, self._debounce_time,"(",ticks_us() - self._last_press > self._debounce_time,")")
        if ticks_ms() - self._last_press > self._debounce_time:
            self._last_press = ticks_ms()
            return True
        else:

            return False
