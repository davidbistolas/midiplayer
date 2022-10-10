import os

import gc


class Playlist:
    """
    Manage the playlist
    """

    def __init__(self, path="/midi", playlist_file='playlist.txt'):

        sd_contents = os.listdir(path)
        playlist = []
        self.path = path
        if playlist_file in sd_contents:
            with open(self.path + "/" + playlist_file) as f:
                for file in f.read().splitlines():
                    playlist.append(file.strip())
        else:
            for file in sd_contents:
                if not file.startswith("."):
                    if file.endswith(".mid"):
                        playlist.append(file)
            del sd_contents
        for filename in playlist:
            try:
                file_stat = open(self.path + "/" + filename, "rb")
                file_stat.close()

            except OSError:
                playlist = list(filter(lambda a: a != filename, playlist))
            except MemoryError:
                # todo- handle memory errors on screen.
                raise
        gc.collect()
        self._playlist = playlist
        self._current_song_index = 0

    def goto_next_song(self):
        if self._current_song_index < (len(self._playlist) - 1):
            self._current_song_index += 1

    def goto_previous_song(self):
        if self._current_song_index > 0:
            self._current_song_index -= 1

    def get_current_song(self):
        return self._playlist[self._current_song_index]

    def get_previous_song(self):
        if self._current_song_index > 0:
            return self._playlist[self._current_song_index - 1]
        else:
            return "                              "

    def get_next_song(self):
        if self._current_song_index < (len(self._playlist) - 1):
            return self._playlist[self._current_song_index + 1]
        else:
            return "                              "
