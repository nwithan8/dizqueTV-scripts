"""
Find broken media file links in dizqueTV.
"""

import argparse

from plexapi import server
from dizqueTV import API

parser = argparse.ArgumentParser(
    description="Check a dizqueTV channel for broken media file links."
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

broken_programs = []
for program in channel.programs:
    if program.file:  # Skip programs that don't have a file (e.g. filler time)
        # Try to get the associated Plex item by its rating key
        try:
            plex_item = plex.fetchItem(ekey=int(program.ratingKey))
        except:
            # No item by that rating key exists in Plex, so the dizqueTV link is broken
            broken_programs.append(program)
            continue

        # Plex returned None, so the dizqueTV link is broken
        # This probably won't happen (an exception would have been thrown), but just in case
        if not plex_item:
            broken_programs.append(program)
            continue

        # If the Plex item has no locations, the dizqueTV link is broken
        if not plex_item.locations:
            broken_programs.append(program)
            continue

        file_location = plex_item.locations[0]

        # If the Plex item's location doesn't match the dizqueTV link, the dizqueTV link is broken
        if file_location != program.file:
            broken_programs.append(program)
            continue

print(f"Found {len(broken_programs)} broken programs in channel #{args.channel_number}")
for program in broken_programs:
    print(f"{program.full_name}")
