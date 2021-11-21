"""
Create a dizqueTV channel with Plex content that has a specific keyword in its description.

The resulting videos (in the media section parameter) will be compiled
into a single dizqueTV channel.  The channel number & name are also
parameters, but the next higher channel number will be used if the
given input is not available.
"""
from plexapi import server
from dizqueTV import API
import argparse
from progress.bar import Bar

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"


# DO NOT EDIT BELOW THIS LINE
parser = argparse.ArgumentParser()
parser.add_argument("keywords", nargs="*", type=str, help="Keyword to search for in Plex")
parser.add_argument("-s", '--sections',  nargs="+", type=str, required=True, help="Plex media section(s) to use")
parser.add_argument("-N", '--channel_name', nargs="?", type=str, help="name of DizqueTV channel to create")
parser.add_argument("-c", '--channel_number', nargs='?', type=int, default=None, help="DizqueTV channel to add playlist to.")
parser.add_argument("-t", '--token', nargs='?', type=str, default=None, help="Override the script's plex token.")
parser.add_argument("-x", "--shuffle", action="store_true", help="Shuffle items once channel is completed.")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose (for debugging)")
args = parser.parse_args()

if args.token is not None and len(args.token) > 0:
    PLEX_TOKEN = args.token

plex_server = server.PlexServer(PLEX_URL, PLEX_TOKEN)

matching_items = []
for section in args.sections:
    for keyword in args.keywords:
        print(f'Searching for items with "{keyword}" in "{section}"...')
        matching_items.extend(plex_server.library.section(section).search(summary__icontains=keyword))

if not matching_items:
    print("No matching items found.")
    exit(0)

matching_items = list(set(matching_items))  # remove duplicate items

answer = input(f"Found {len(matching_items)} matching items. Proceed with making this channel? [y/n] ")
if type(answer) != str or not answer.lower().startswith('y'):
    exit(0)

dtv = API(url=DIZQUETV_URL, verbose=args.verbose)
new_channel_number = args.channel_number
channel_name = args.channel_name
final_programs = []
for item in matching_items:
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
if not new_channel:
    print("Failed to create channel.")
    exit(1)


print(f"Channel {new_channel_number} '{channel_name}' successfully created.")
if args.shuffle:
    print("Shuffling channel items...")
    new_channel.sort_programs_randomly()

