import gc
from machine import Pin

from hardware import tm1637


class LedDisplay:
    """
    Baseclass for 4x 7 segment display
    """

    def __init__(self, clock, data):
        clock_pin = Pin(clock)
        data_pin = Pin(data)
        self._display = tm1637.TM1637(clk=clock_pin, dio=data_pin)
        gc.collect()

    def set(self, value):
        self._display.show(value)

    def clear(self):
        self._display.show("----")


class LedDisplayTime(LedDisplay):
    """
    Time display.
    """

    def set(self, value):
        """
        Args:
            value: string in MM:SS format
        Returns:
        """
        minutes = int(value.split(":")[0])
        seconds = int(value.split(":")[1])
        self._display.numbers(minutes, seconds)


class LedDisplayBPM(LedDisplay):
    """
    BPM Display
    """

    def set(self, value):
        self._display.show("{:>04d}".format(value))
