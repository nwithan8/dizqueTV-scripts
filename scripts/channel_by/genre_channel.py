"""
Make a dizqueTV channel for a particular movie studio, TV network or streaming platform
(i.e. Sony Pictures, Columbia Pictures, NBC, Comedy Central, Netflix, Apple TV+).
Grabs all items from your Plex library associated with that studio/network/platform.
Creates a dizqueTV channel with all the items.
dizqueTV channel will be named after the studio/network/platform
"""

import argparse
from urllib.parse import quote

from dizqueTV import API
from plexapi import server


# Complete this function
def get_items(args: argparse.Namespace) -> list:
    """
    Get all items matching the given parameters.
    :return: List of Plex items
    """
    items = []
    for section in args.sections:
        for genre in args.genres:
            print(f"Looking up content in {section} in the {genre} genre...")
            genre_items = plex_server.library.section(section).search(genre=f"{quote(genre)}")
            if genre_items:
                print("Matching GENRE items:")
                for item in genre_items:
                    print(f"{genre} - {item.title}")
                items.extend(genre_items)
    return items


# Complete this function
def get_channel_name(args: argparse.Namespace) -> str:
    """
    Get the name of the channel to create.
    :return: Channel name
    """
    return args.channel_name or ", ".join(name for name in args.genres)


# Add any additional arguments you need
parser = argparse.ArgumentParser(
    description="Create a dizqueTV channel for a particular genre."
)
parser.add_argument('genres', nargs="+", type=str, help="genres to find items from")
parser.add_argument("-s", '--sections', nargs="+", type=str, required=True, help="Plex media section(s) to use")

# DO NOT EDIT BELOW THIS LINE
parser.add_argument('-d', '--dizquetv_url', type=str, required=True, help="URL of dizqueTV server")
parser.add_argument('-p', '--plex_url', type=str, required=True, help="URL of Plex server")
parser.add_argument("-t", '--plex_token', type=str, required=True, help="Plex server token")
parser.add_argument("-n", '--channel_name', nargs="?", type=str, help="name of dizqueTV channel to create")
parser.add_argument("-c", '--channel_number', nargs='?', type=int, default=None,
                    help="dizqueTV channel to add playlist to.")
parser.add_argument("-x", "--shuffle", action="store_true", help="Shuffle items once channel is completed.")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose (for debugging)")
args = parser.parse_args()

dtv = API(url=args.dizquetv_url, verbose=args.verbose)

plex_server = server.PlexServer(args.plex_url, args.plex_token)


def main(args: argparse.Namespace) -> None:
    # Get all items matching the given parameters
    matching_items = get_items(args)
    if not matching_items:
        print("No matching items found.")
        exit(0)

    # Clean up the list of items
    matching_items = list(set(matching_items))  # remove duplicate items

    # Verify that the user wants to proceed
    answer = input(f"Found {len(matching_items)} matching items. Proceed with making this channel? [y/n] ")
    if type(answer) != str or not answer.lower().startswith('y'):
        exit(0)

    # Copy the items to a dizqueTV channel
    new_channel_number = args.channel_number
    channel_name = get_channel_name(args)
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

    if new_channel_number in dtv.channel_numbers:
        channel = dtv.get_channel(channel_number=new_channel_number)
        channel.add_programs(programs=final_programs, plex_server=plex_server)
    else:
        channel = dtv.add_channel(programs=final_programs,
                                  plex_server=plex_server,
                                  number=new_channel_number,
                                  name=f"{channel_name}",
                                  handle_errors=True)

    if not channel:
        print("Failed to update channel.")
        exit(1)

    print(f"Channel {new_channel_number} '{channel_name}' successfully updated.")

    # Shuffle the channel if requested
    if args.shuffle:
        print("Shuffling channel items...")
        channel.sort_programs_randomly()


main(args=args)
