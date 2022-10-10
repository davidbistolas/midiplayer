import gc
import machine
import os

from hardware import sdcard


class SDCard:
    """
    SD Card Interface
    """

    def __init__(self, cs, sck, mosi, miso):
        cs = machine.Pin(cs, machine.Pin.OUT)
        sd_spi = machine.SPI(1, baudrate=60000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB,
                             sck=machine.Pin(sck), mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self._sd = sdcard.SDCard(sd_spi, cs)
        self._vfs = os.VfsFat(self._sd)
        gc.collect()

    def mount(self, mount_point, readonly=True):
        os.mount(self._sd, mount_point, readonly=readonly)
