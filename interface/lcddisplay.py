import gc
from machine import SPI, Pin

from hardware.ili9341 import Display, color565
from hardware.xglcd_font import XglcdFont


class LCDDisplay:
    """
    4.2" LCD Display
    """

    def __init__(self, sck, mosi, miso, dc, cs, rst, colours=None):
        disp_spi = SPI(0,
                       baudrate=15000000,
                       polarity=1,
                       phase=1,
                       bits=8,
                       firstbit=SPI.MSB,
                       sck=Pin(sck),
                       mosi=Pin(mosi),
                       miso=Pin(miso))

        self._display = Display(disp_spi, dc=Pin(dc), cs=Pin(cs), rst=Pin(rst), height=240, width=320, rotation=270)
        self.font = self.load_font("/fonts/Unispace12x24.c", 12, 24)
        self.colours = colours
        self.previous = ""
        self.current = ""
        self.next = ""
        gc.collect()

    @staticmethod
    def load_font(font, height, width):
        return XglcdFont(font, height, width)

    def clear(self):
        self._display.clear(0)
        self._display.fill_rectangle(0, 30, 319, 60, self.colours.background_variant)
        self._display.fill_rectangle(0, 90, 319, 60, self.colours.background)
        self._display.fill_rectangle(0, 150, 319, 60, self.colours.background_variant)

    def show_splash(self, song_name):
        self._display.clear(0)
        name = song_name.split(".")[0].strip()
        start = self.get_centre_distance(name)
        self._display.draw_text(start, 90, name, self.font,
                                color565(255, 255, 255), landscape=False)

    def get_centre_distance(self, name):
        # 26 characters wide
        word_width = len(name) * self.font.width
        return round((self._display.width / 2) - (word_width / 2))

    def draw_previous(self, song_name):
        name = song_name.split(".")[0].strip()
        start = self.get_centre_distance(name)
        previous_start = self.get_centre_distance(self.previous)
        # self._display.fill_rectangle(0, 30, 319, 60, self.colours.background_variant)
        self._display.draw_text(previous_start, 45, self.previous, self.font,
                                self.colours.background_variant, landscape=False,
                                background=self.colours.background_variant)
        self._display.draw_text(start, 45, name, self.font,
                                self.colours.foreground_variant, landscape=False,
                                background=self.colours.background_variant)
        self.previous = name

    def draw_current(self, song_name):
        name = song_name.split(".")[0].strip()
        start = self.get_centre_distance(name)
        current_start = self.get_centre_distance(self.current)
        # self._display.fill_rectangle(0, 90, 319, 60, self.colours.background)
        self._display.draw_text(current_start, 105, name, self.font,
                                self.colours.background, landscape=False,
                                background=self.colours.background)
        self._display.draw_text(start, 105, name, self.font,
                                self.colours.foreground, landscape=False,
                                background=self.colours.background)
        self.current = name

    def draw_next(self, song_name):
        name = song_name.split(".")[0].strip()
        start = self.get_centre_distance(name)
        next_start = self.get_centre_distance(self.next)
        # self._display.fill_rectangle(0, 150, 319, 60, self.colours.background_variant)
        self._display.draw_text(next_start, 165, self.next, self.font,
                                self.colours.background_variant, landscape=False,
                                background=self.colours.background_variant)
        self._display.draw_text(start, 165, name, self.font,
                                self.colours.foreground_variant, landscape=False,
                                background=self.colours.background_variant)
        self.next = name
