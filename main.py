import gc
from math import floor
from time import ticks_us, sleep_us, sleep_ms

import machine
from machine import Pin
from machine import Timer

from interface.buttons import SimpleButton
from interface.colours import DisplayColours
from interface.lcddisplay import LCDDisplay
from interface.rgbled import RgbLed
from interface.sdcard import SDCard
from interface.sevensegmentdisplay import LedDisplayTime, LedDisplayBPM
from pedal.decorators import threadsafe
from pedal.player import Player
from pedal.playlist import Playlist


class MidiPlayer:
    """
    The MidiPedal App.
    """

    def __init__(self):

        # garbage collection. I think I have a memory leak

        gc.enable()
        self.play_color = "#002200"
        self.tempo_color = "#009900"
        self.stop_color = "#990000"

        # Hardware Setup
        # self.midi_out = machine.UART(1, 31250)
        self.rgb_led = RgbLed(20, 21, 22)
        self.bpm_display = LedDisplayBPM(2, 3)
        self.time_display = LedDisplayTime(0, 1)

        # "ZERO THE BOARD"
        # Set LED to "blue", cos we're booting up.

        self.rgb_led.set(self.stop_color)

        # tempo and bmp zeroed out

        self.bpm_display.clear()
        self.time_display.set("00:00")

        self.sd_card = SDCard(9, 10, 11, 8)
        self.sd_card.mount("/storage")

        # self.sd_card.copy_files()

        # Set up buttons
        self.transport_btn = SimpleButton(machine.Pin(26, Pin.IN, Pin.PULL_DOWN),
                                          callback=self.transport,
                                          bounce_time=250,
                                          )

        self.next_btn = SimpleButton(machine.Pin(27, Pin.IN, Pin.PULL_DOWN),
                                     self.next_song,
                                     bounce_time=250)

        self.prev_btn = SimpleButton(machine.Pin(28, Pin.IN, Pin.PULL_DOWN),
                                     self.last_song,
                                     bounce_time=250)

        # Set up the displays

        colours = DisplayColours("#FFFFFF", "#212783", -16)

        # sck, mosi, miso, dc, cs, rst,
        self.screen = LCDDisplay(18, 19, 16, 15, 17, 14, colours=colours)
        self.screen.show_splash("Midi Player v2r17")

        self.playlist = Playlist(path="/storage", playlist_file="playlist.txt")

        self.player = Player(self.playlist, self)

        self.current_time = 0
        self.current_tempo = -1

        # transport/playlist control
        self.is_playing = False
        self.is_stopped = True
        self.go_to_next_song = False
        self.go_to_previous_song = False
        self.start_playing = False
        self.stop_playing = False

        self.bpm_time_offset = 250000
        self.last_loop_utime = ticks_us()
        # self.play_task_iter = 0
        self.last_time = "00:00"
        self.last_tempo = 120

        gc.collect()

    @staticmethod
    def tempo_to_bpm(tempo):
        """
        Convert MIDI tempo to BPM.
        returns: integer
        """

        if tempo == 0:
            return 0
        else:
            # One minute is 60 million microseconds.
            return floor(60000000 / tempo)

    # @threadsafe
    def next_song(self):
        self.go_to_next_song = True

    # @threadsafe
    def last_song(self):
        self.go_to_previous_song = True

    # @threadsafe
    def transport(self):
        if self.is_playing:
            self.stop_playing = True
        else:
            self.start_playing = True

    def stop(self):
        if self.is_playing:
            self.player.stop()
        self.is_playing = False
        # self.current_tempo = 0
        self.bpm_display.clear()
        self.rgb_led.set(self.stop_color)
        # self.player = None
        gc.collect()

    def play(self):
        if self.is_playing:
            self.stop()
        self.player.play()
        self.rgb_led.set(self.play_color)

    def display_tempo(self,timer=None):
        if self.current_tempo > 0:
            bpm = self.tempo_to_bpm(self.current_tempo)
            self.bpm_display.set(bpm)
            self.last_tempo = bpm;
            self.bpm_time_offset = (1 / (bpm / 60)) * 1000000
        else:
            self.bpm_display.clear()

    def set_tempo(self, tempo):
        self.current_tempo = tempo
        bpm = self.tempo_to_bpm(tempo)
        self.bpm_time_offset = (1 / (bpm / 60)) * 1000000

    def display_time(self, timer=None):
        if self.is_playing:
            seconds_played = floor(self.current_time / 1000000)
            minutes = floor(seconds_played / 60)
            seconds = seconds_played - (60 * minutes)
            current_time_string = "{:>02d}:{:>02d}".format(minutes, seconds)
            if self.last_time != current_time_string:
                self.time_display.set(current_time_string)
                self.last_time = current_time_string
        else:
            self.time_display.set("00:00")

    def set_time(self, current_time):
        self.current_time = current_time

    # @threadsafe
    def display_playlist(self, timer=None):
        self.screen.draw_current(self.playlist.get_current_song())
        self.screen.draw_previous(self.playlist.get_previous_song())
        self.screen.draw_next(self.playlist.get_next_song())
        # bpm = self.tempo_to_bpm(self.current_tempo)
        # self.bpm_display.set(bpm)

    # @threadsafe
    def handle_transport_controls(self,timer=None):
        if self.go_to_next_song:
            self.go_to_next_song = False
            self.stop()
            self.playlist.goto_next_song()
            self.display_playlist()

        elif self.go_to_previous_song:
            self.go_to_previous_song = False
            self.stop()
            self.playlist.goto_previous_song()
            self.display_playlist()

        elif self.start_playing:
            self.start_playing = False
            self.is_playing = True
            self.play()

        elif self.stop_playing:
            self.stop_playing = False
            self.stop()

        elif self.is_stopped:
            self.is_playing = False
            self.is_stopped = False
            self.stop()

    def tempo_light(self, timer=None):
        if self.is_playing:
            now = ticks_us()
            offset = now - self.last_loop_utime
            self.last_loop_utime = now
            if offset > self.bpm_time_offset:
                if self.rgb_led.get() != self.tempo_color:
                    self.rgb_led.set(self.tempo_color)
                else:
                    self.rgb_led.set(self.play_color)

            sleep_us(int(self.bpm_time_offset))
            gc.collect()
        else:
            sleep_ms(500)

    def update_status(self, status):
        self.current_tempo = status["tempo"]
        self.current_time = status["time"]
        self.is_playing = status["playing"]
        self.is_stopped = not status["playing"]

    def run(self):
        self.rgb_led.set(app.stop_color)
        self.screen.clear()
        self.display_playlist()
        time_display_timer = Timer(period=1000, mode=Timer.PERIODIC, callback=self.display_time)
        tempo_display_timer = Timer(period=1000, mode=Timer.PERIODIC, callback=self.display_tempo)
        transport_timer = Timer(period=500, mode=Timer.PERIODIC, callback=self.handle_transport_controls)
        while True:
            self.tempo_light()


machine.freq(280000000)

app = MidiPlayer()
app.run()
