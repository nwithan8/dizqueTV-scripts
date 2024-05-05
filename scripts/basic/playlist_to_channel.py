"""
Copy all items from a Plex playlist to an existing dizqueTV channel.
Refreshes the channel (removes all existing programs, re-adds new items)
"""

from typing import List, Union
import argparse

from plexapi import server, playlist
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"

parser = argparse.ArgumentParser()
parser.add_argument('playlist_name',
                    type=str,
                    help="Name of Plex playlist to convert to a channel")
parser.add_argument('-c',
                    '--channel_number',
                    nargs='?',
                    type=int,
                    default=None,
                    help="dizqueTV channel to add playlist to.")
parser.add_argument("-s",
                    "--shuffle",
                    action="store_true",
                    help="Shuffle items once channel is completed.")
parser.add_argument("-v",
                    "--verbose",
                    action="store_true",
                    help="Verbose (for debugging)")
args = parser.parse_args()


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


dtv = API(url=DIZQUETV_URL, verbose=args.verbose)
plex = Plex(url=PLEX_URL,
            token=PLEX_TOKEN)
plex_playlist = plex.get_playlist(playlist_name=args.playlist_name)
first_needed = False
if args.channel_number:
    channel = dtv.get_channel(channel_number=args.channel_number)
    if not channel:
        print(f"Could not find channel #{args.channel_number}")
        exit(1)
else:
    first_needed = True
    channel_numbers = dtv.channel_numbers
    if channel_numbers:
        new_channel_number = max(channel_numbers) + 1
    else:
        new_channel_number = 1
to_add = []
if plex_playlist:
    plex_playlist_items = plex_playlist.items() # preload to avoid connection closed while looping
    for item in plex_playlist_items:
        item = dtv.convert_plex_item_to_program(plex_item=item,
                                                plex_server=plex.server)
        if item:
            if first_needed:
                print(f"Creating '{plex_playlist.title}' channel on dizqueTV...")
                channel = dtv.add_channel(programs=[item],
                                          name=plex_playlist.title,
                                          number=new_channel_number)
                first_needed = False
            print(f"Adding {item.full_name}...")
            to_add.append(item)
    if channel.delete_all_programs():
        dtv.add_programs_to_channels(programs=to_add,
                                     channels=[channel])
        if args.shuffle:
            channel.sort_programs_randomly()
else:
    print(f"Could not find {args.playlist_name} playlist.")
