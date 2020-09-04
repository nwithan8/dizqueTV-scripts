"""
Copy all items from a Plex playlist to an existing dizqueTV channel.
Refreshes the channel (removes all existing programs, re-adds new items)
"""

from typing import List, Union

from plexapi import server, playlist
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"
DIZQUETV_CHANNEL_NUMBER = 1

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"
PLAYLIST_NAME = "mysmartplaylist"


class Plex:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.server = server.PlexServer(url, token)

    def get_playlists(self) -> List[playlist.Playlist]:
        return self.server.playlists()

    def get_playlist(self, playlist_name: str) -> Union[playlist.Playlist, None]:
        for playlist in self.get_playlists():
            if playlist.title == playlist_name:
                return playlist
        return None


dtv = API(url=DIZQUETV_URL)
plex = Plex(url=PLEX_URL, token=PLEX_TOKEN)
plex_playlist = plex.get_playlist(playlist_name=PLAYLIST_NAME)
channel = dtv.get_channel(channel_number=DIZQUETV_CHANNEL_NUMBER)
to_add = []
if channel:
    if plex_playlist:
        for item in plex_playlist.items():
            item = dtv.convert_plex_item_to_program(plex_item=item, plex_server=plex.server)
            if item:
                print(f"Adding {item.title}...")
                to_add.append(item)
        if channel.delete_all_programs():
            dtv.add_programs_to_channels(programs=to_add, channels=[channel])
    else:
        print(f"Could not find {PLAYLIST_NAME} playlist.")
else:
    print(f"Could not find channel #{DIZQUETV_CHANNEL_NUMBER}")
