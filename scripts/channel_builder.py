"""
Create a dizqueTV channel by searching Plex for provided inputs:
 - Studio (Paramount, Netflix, etc.)
 - Genre (Western, Sci-Fi, etc.)
 - Collection (Tags defined by the user in Plex)

The resulting videos (in the media section parameter) will be compiled
into a single dizqueTV channel.  The channel number & name are also
parameters, but the next higher channel number will be used if the
given input is not available.
"""

from typing import List, Union

from plexapi import server, media, library, playlist, myplex
from dizqueTV import API
import argparse
from urllib.parse import quote

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"

#

parser = argparse.ArgumentParser()
parser.add_argument("-S", "--studio",
                    nargs="*", type=str,
                    help="name of studios, networks or platforms to find items from")
parser.add_argument("-G", '--genre',
                    nargs="*", type=str,
                    help="name of genre to find items from")
parser.add_argument("-C", '--collection',
                    nargs = "*", type=str,
                    help="name of collection to find items from")
parser.add_argument("-s", '--section',
                    nargs="+", type=str, required=True,
                    help="Plex media section(s) to use")
parser.add_argument("-N", '--channel_name',
                    nargs="?", type=str,
                    help="name of DizqueTV channel to create")
parser.add_argument("-c", '--channel_number',
                    nargs='?', type=int,
                    default=None, help="DizqueTV channel to add playlist to.")
parser.add_argument("-x", "--shuffle",
                    action="store_true",
                    help="Shuffle items once channel is completed.")
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Verbose (for debugging)")
args = parser.parse_args()

#channel_name = ", ".join(name for name in args.studio)

plex_server = server.PlexServer(PLEX_URL, PLEX_TOKEN)

if args.studio is None and args.genre is None and args.collection is None:
    print(f"Either studio, genre or collection must be passed in. Exiting.")
    exit(1)

all_items = []
for section in args.section:
    if args.studio is not None:
        for studio in args.studio:
            print(f"Looking up content from {studio}...")
            studio_items = plex_server.library.section(section).search(studio=f"{quote(studio)}")
            if studio_items:
                print("Matching STUDIO items:")
                for item in studio_items:
                    print(f"{item.studio} - {item.title}")
                all_items.extend(studio_items)

    if args.genre is not None:
        for genre in args.genre:
            genre_items = plex_server.library.section(section).search(genre=f"{quote(genre)}")
            if genre_items:
                print("Matching GENRE items:")
                for item in genre_items:
                    print(f"{genre} - {item.title}")
                all_items.extend(genre_items)

    if args.collection is not None:
        for collection in args.collection:
            found_coll = plex_server.library.section(section).search(title=collection, libtype='collection')
            if found_coll and len(found_coll) == 1:
                print("Matching COLLECTION items:")
                for item in found_coll[0].children:
                    print(f"{collection_parm} - {item.title}")
                all_items.extend(found_coll[0].children)

if all_items:
    answer = input("Would you like to proceed with making the channel? (Y/N) ")
    if type(answer) == str and answer.lower().startswith('y'):
        dtv = API(url=DIZQUETV_URL, verbose=args.verbose)
        new_channel_number = args.channel_number
        channel_name = args.channel_name
        final_programs = []
        for item in all_items:
            if item.type == 'movie':
                final_programs.append(item)
            elif item.type == 'show':
                print(f"Grabbing episodes of {item.title}...")
                for episode in item.episodes():
                    if (hasattr(episode, "originallyAvailableAt") and episode.originallyAvailableAt) and \
                            (hasattr(episode, "duration") and episode.duration):
                        final_programs.append(episode)
        new_channel = dtv.add_channel(programs=final_programs,
                                      plex_server=plex_server,
                                      number=new_channel_number,
                                      name=f"{channel_name}",
                                      handle_errors=True)
        if new_channel:
            print(f"Channel {new_channel_number} '{channel_name}' successfully created.")
            if args.shuffle:
                new_channel.sort_programs_randomly()
        else:
             print("Something went wrong.")
    else:
            exit(0)
else:
    print(f"Could not find any media items from given arguments. Exiting.")
