"""
Fix broken media file links in dizqueTV.
"""

import argparse

from dizqueTV import API
from plexapi import server

parser = argparse.ArgumentParser(
    description="Fix a dizqueTV channel with broken media file links."
)
parser.add_argument("channel_number", type=int, help="Channel number to check for broken links.")
parser.add_argument('-d', '--dizquetv_url', type=str, required=True, help="URL of dizqueTV server")
parser.add_argument('-p', '--plex_url', type=str, required=True, help="URL of Plex server")
parser.add_argument("-t", '--plex_token', type=str, required=True, help="Plex server token")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose (for debugging)")
args = parser.parse_args()

dtv = API(url=args.dizquetv_url, verbose=args.verbose)
plex = server.PlexServer(baseurl=args.plex_url, token=args.plex_token)

channel = dtv.get_channel(channel_number=args.channel_number)
if not channel:
    print(f"Could not find channel #{args.channel_number}")
    exit(1)

fixed_programs = []
unfixed_programs = []
for program in channel.programs:
    if program.file:  # Skip programs that don't have a file (e.g. filler time)
        # Try to get the associated Plex item by its rating key
        try:
            plex_item = plex.fetchItem(ekey=int(program.ratingKey))
        except:
            # No item by that rating key exists in Plex, so the dizqueTV link is broken
            print(f"Could not find Plex item with rating key {program.ratingKey}, skipping...")
            unfixed_programs.append(program)
            continue

        # Plex returned None, so the dizqueTV link is broken
        # This probably won't happen (an exception would have been thrown), but just in case
        if not plex_item:
            print(f"Could not find Plex item with rating key {program.ratingKey}, skipping...")
            unfixed_programs.append(program)
            continue

        # If the Plex item has no locations, the dizqueTV link is broken
        if not plex_item.locations:
            print(f"Plex item with rating key {program.ratingKey} has no file locations, skipping...")
            unfixed_programs.append(program)
            continue

        plex_file = plex_item.media[0].parts[0].key
        file = plex_item.media[0].parts[0].file
        icon_url = plex_item.thumbUrl

        # If the Plex item's location doesn't match the dizqueTV link, the dizqueTV link is broken
        if file != program.file:
            print(f"Plex item with rating key {program.ratingKey} has a different file location, updating...")
            program.update(file=file, plexFile=plex_file, icon=icon_url)
            fixed_programs.append(program)
            continue

if fixed_programs:
    print(f"Updated {len(fixed_programs)} broken programs in channel #{args.channel_number}")

if unfixed_programs:
    print(f"Could not update {len(unfixed_programs)} broken programs in channel #{args.channel_number}")
    for program in unfixed_programs:
        print(f"{program.full_name}")
