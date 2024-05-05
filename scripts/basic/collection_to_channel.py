"""
Copy all items from a Plex playlist to an existing dizqueTV channel.
Refreshes the channel (removes all existing programs, re-adds new items)
"""

import argparse
from typing import List, Union

from dizqueTV import API
from plexapi import video, audio, server, collection

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"

parser = argparse.ArgumentParser()
parser.add_argument('collection_name',
                    type=str,
                    help="Name of Plex collection to convert to a channel")
parser.add_argument('collection_section',
                    type=str,
                    help="Name of Plex Library the target collection belongs to")
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
    def __init__(self, url: str, token: str):
        self.url: str = url
        self.token: str = token
        self.server: server.PlexServer = server.PlexServer(url, token)

    def get_collections_for_section(self, section_name: str) -> List[collection.Collection]:
        for section in self.server.library.sections():
            if section.title == section_name:
                return section.collections()
        return []

    def get_collection(self, collection_name: str, collection_section_name: str) -> Union[collection.Collection, None]:
        for col in self.get_collections_for_section(section_name=collection_section_name):
            if col.title == collection_name:
                return col
        return None


dtv = API(url=DIZQUETV_URL, verbose=args.verbose)
plex = Plex(url=PLEX_URL,
            token=PLEX_TOKEN)
plex_collection = plex.get_collection(collection_name=args.collection_name,
                                      collection_section_name=args.collection_section)
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
if plex_collection:
    plex_collection_items: List[
        video.Movie | video.Episode | video.Show | audio.Track | audio.Artist | audio.Album] = plex_collection.items()  # preload to avoid connection closed while looping
    file_items = []
    for item in plex_collection_items:
        # collect all episodes of a show/season
        if item.type in ['show', 'season']:
            file_items.extend(item.episodes())
        # collect all tracks of an artist/album
        elif item.type in ['artist', 'album']:
            file_items.extend(item.tracks())
        # add movies and clips directly
        else:
            file_items.append(item)
    for item in file_items:  # Movie, Episode and Track objects
        item = dtv.convert_plex_item_to_program(plex_item=item,
                                                plex_server=plex.server)
        if item:
            if first_needed:
                print(f"Creating '{plex_collection.title}' channel on dizqueTV...")
                channel = dtv.add_channel(programs=[item],
                                          name=plex_collection.title,
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
