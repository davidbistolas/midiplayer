import gc

from hardware.ili9341 import color565


class DisplayColours:
    """
    Setup Display Theme - automatically dims the same colours for a nice Commodore64 look
    """

    def __init__(self, foreground, background, dim_offset=-1):
        (fr, fg, fb) = self._hex_to_rgb(foreground)
        (vfr, vfg, vfb) = self._hex_to_rgb(self.color_variant(foreground, brightness_offset=dim_offset))

        (br, bg, bb) = self._hex_to_rgb(background)
        (vbr, vbg, vbb) = self._hex_to_rgb(self.color_variant(background, brightness_offset=dim_offset))
        self.foreground = color565(fr, fg, fb)
        self.foreground_variant = color565(vfr, vfg, vfb)
        self.background = color565(br, bg, bb)
        self.background_variant = color565(vbr, vbg, vbb)
        gc.collect()

    @staticmethod
    def _hex_to_rgb(hex_code):
        h = hex_code.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def color_variant(self, colour, brightness_offset=1):
        """
        takes a hex colour and returns a lighter or darker variant of it
        """
        original_rgb = self._hex_to_rgb(colour)
        # this needs to drop the same *relative( amount in all three values
        variant = [value + brightness_offset for value in original_rgb]
        variant = [min([255, max([0, i])]) for i in variant]  # make sure new values are between 0 and 255
        return "#" + "".join([hex(i)[2:] for i in variant])
