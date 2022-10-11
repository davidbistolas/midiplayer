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

    def __init__(self, playlist, interface, midi_out=1):
        self.thread = None
        self.midi_out = machine.UART(midi_out, 31250, txbuf=1024)
        self.is_playing = False
        self.utime_played = 0
        self.current_tempo = -1
        self.tempo_offset = 1
        self.playlist = playlist
        self.filename = self.playlist.path + "/" + self.playlist.get_current_song()
        self.current_tempo=0
        self.interface = interface
        self.update_status()


    @threadsafe
    def update_status(self):
        status = {"playing": self.is_playing, "tempo": self.current_tempo, "time": self.utime_played}
        print("player.update_status - updating status with ", status)
        self.interface.update_status(status)

    def stop(self):
        # print("player.stop() Called", self.queue)
        self.is_playing = False
        self.utime_played = 0
        self.current_tempo = 0
        self.is_playing = False
        self.update_status()
        # print("player.stop()", self.queue)
        gc.collect()

    def play(self):
        gc.collect()
        print("player.play() - Starting Player for :",self.playlist.get_current_song())
        self.filename = self.playlist.path + "/" + self.playlist.get_current_song()
        self.utime_played = 0
        if not self.is_playing:
            self.is_playing = True
            self.update_status()
            self.thread = _thread.start_new_thread(self._play, ())

    def _play(self):
        player = umidiparser.MidiFile(self.filename)
        for event in player:
            if self.is_playing:
                # delta = round(event.delta_us * self.tempo_offset)
                self.utime_played += event.delta_us
                # self.parent.display_time()
                if event.is_tempo():
                    self.current_tempo = event.tempo

                if event.is_end():
                    self.utime_played = 0
                    self.is_playing = False
                    print("player._play() Exiting thread due to song end")
                    self.update_status()

                    break

                self.midi_out.write(event.to_midi())
                utime.sleep_us(event.delta_us)

            else:
                self.utime_played = 0
                self.is_playing = False
                gc.collect()
                # self.midi_out.deinit()
                print("player._play() - Exiting thread due to abrupt stop")
                self.update_status()

                break

            self.update_status()

        # print("player._play() - TODO Send the all-notes-off message here.")
