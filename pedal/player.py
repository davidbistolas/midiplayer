import gc

import _thread
import machine
from pedal import umidiparser
import utime
from pedal.decorators import threadsafe

class Player:
    """
    The actual MIDI player
    """

    def __init__(self, playlist, interface, uart=1):
        self.thread = None
        self.uart = uart
        self.midi_out = machine.UART(self.uart, 31250, txbuf=1024)

        self.is_playing = False
        self.utime_played = 0
        self.tempo_offset = 1
        self.playlist = playlist
        self.filename = self.playlist.path + "/" + self.playlist.get_current_song()
        self.player =None;
        self.current_tempo=0
        self.interface = interface
        # self.update_status()


    @threadsafe
    def update_status(self):
        status = {"playing": self.is_playing, "tempo": self.current_tempo, "time": self.utime_played}
        self.interface.update_status(status)

    def stop(self):
        self.is_playing = False
        self.utime_played = 0
        self.current_tempo = 0
        self.update_status()
        gc.collect()

    def play(self):
        gc.collect()
        self.filename = self.playlist.path + "/" + self.playlist.get_current_song()
        self.player = umidiparser.MidiFile(self.filename)
        self.utime_played = 0
        if not self.is_playing:
            self.is_playing = True
            self.update_status()
            self.thread = _thread.start_new_thread(self._play, ())

    def _play(self):
        for event in self.player:
            if self.is_playing:
                # delta = round(event.delta_us * self.tempo_offset)
                self.utime_played += event.delta_us
                # self.parent.display_time()
                if event.is_tempo():
                    self.current_tempo = event.tempo
                    self.update_status()

                if event.is_end():
                    self.utime_played = 0
                    self.is_playing = False
                    self.update_status()
                    gc.collect()  # pretty sure GC isn't working on core1.
                    _thread.exit()
                    return

                self.update_status()
                self.midi_out.write(event.to_midi())
                utime.sleep_us(event.delta_us)

            else:
                self.utime_played = 0
                self.is_playing = False
                self.update_status()
                gc.collect()
                # self.midi_out.deinit()
                _thread.exit()
                return
        self.update_status()
        # print("player._play() - TODO Send the all-notes-off message here.")
        gc.collect() # pretty sure GC isn't working on core1.
        _thread.exit()
        return
