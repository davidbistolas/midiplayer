import time

import gc
from machine import Pin, Timer
from time import ticks_us


class ShortLongButton:
    """
    Hardware Button with debounce and long/short press support
    """

    def __init__(self, pin, short_callback, long_callback, short_duration_ms=150, long_duration_ms=500,
                 pin_logic_pressed=False, debounce_ms=100):
        self.pin_logic_pressed = pin_logic_pressed
        self.debounce_ms = debounce_ms
        self.short_callback = short_callback
        self.short_duration = short_duration_ms
        self.long_duration = long_duration_ms
        self.long_callback = long_callback
        self.last_release_ms = 0
        self.last_press_ms = 0

        self.pin = pin
        self.pin.irq(self._button_handler, Pin.IRQ_FALLING | Pin.IRQ_RISING)

        self.db_timer = Timer(-1)
        self.expected_value = True

    def _debounce_timer_expired(self, event):

        if self.pin.value() == self.pin_logic_pressed:
            current_value = True
        else:
            current_value = False

        if self.expected_value and current_value:
            self.expected_value = False
            self.last_press_ms = time.ticks_ms()
            if self.last_release_ms == 0:
                ms_since_last_press = 0
            else:
                ms_since_last_press = time.ticks_diff(self.last_press_ms, self.last_release_ms) + 2 * self.debounce_ms
            self.__callback_handler(self.pin, True, ms_since_last_press)

        elif (not self.expected_value) and (not current_value):
            self.expected_value = True
            self.last_release_ms = time.ticks_ms()
            ms_duration_of_press = time.ticks_diff(self.last_release_ms, self.last_press_ms) + 2 * self.debounce_ms
            self.__callback_handler(self.pin, False, ms_duration_of_press)
        # else:
        # print("Missed edge: expected:", self.expected_value, " actual:", current_value)

        # Re-enable pin interrupt
        self.pin.irq(self._button_handler, Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def __callback_handler(self, pin, pressed, duration_ms):
        if pressed:
            if duration_ms < self.long_duration:
                self.short_callback()
            else:
                self.long_callback()

    def _button_handler(self, event):
        self.db_timer.init(mode=Timer.ONE_SHOT, period=self.debounce_ms, callback=self._debounce_timer_expired)

        # Disable pin interrupt
        self.pin.irq(trigger=0)


class SimpleButton:
    """
    Hardware Button, with debounce
    """

    def __init__(self, pin, callback=None, bounce_time=45):
        self.button = pin
        self.callback = callback
        self.button.irq(trigger=Pin.IRQ_RISING, handler=self.on_press)
        self._last_press = 0
        self._debounce_time = bounce_time * 10000.0
        self._last_press = 0.0

        gc.collect()

    def on_press(self, event):

        if self.debounce():
            self.callback()

    def debounce(self):
        if ticks_us() - self._last_press > self._debounce_time:
            self._last_press = ticks_us()
            return True
        else:
            return False
