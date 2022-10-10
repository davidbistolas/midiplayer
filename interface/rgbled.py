import gc
from machine import Pin, PWM


class RgbLed:
    """
    Baseclass for RGB LED. Works will common cathode and anode - although
    For common anode displays it is limited to red, purple, blue, cyan, green, yellow, white and off.
    """

    def __init__(self, red_pin, green_pin, blue_pin, frequency=100000, cathode=True):

        self.cathode = cathode
        self.colour = "#000000"

        if self.cathode:
            red_pin = Pin(red_pin, Pin.OUT)
            green_pin = Pin(green_pin, Pin.OUT)
            blue_pin = Pin(blue_pin, Pin.OUT)
            self._red = PWM(red_pin)
            self._red.freq(frequency)
            self._green = PWM(green_pin)
            self._green.freq(frequency)
            self._blue = PWM(blue_pin)
            self._blue.freq(frequency)

        else:
            red_pin = Pin(red_pin, Pin.OUT)
            green_pin = Pin(green_pin, Pin.OUT)
            blue_pin = Pin(blue_pin, Pin.OUT)
            self._red = red_pin
            self._green = green_pin
            self._blue = blue_pin
        gc.collect()

    def get(self):
        return self.colour

    def set(self, hex_code):
        self.colour = hex_code
        (r, g, b) = self._hex_to_rgb(hex_code)

        if self.cathode:
            self._red.duty_u16(((r + 1) * 256) - 1)
            self._green.duty_u16(((g + 1) * 256) - 1)
            self._blue.duty_u16(((b + 1) * 256) - 1)
        else:
            self._red.value(not (r > 0))
            self._green.value(not (g > 0))
            self._blue.value(not (b > 0))

    @staticmethod
    def _hex_to_rgb(hex_code):
        h = hex_code.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
