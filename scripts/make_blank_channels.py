"""
Make "blank" channels on dizqueTV
Each channel will have a single default Flex time.
"""

from typing import List, Union
import argparse

from plexapi import server, playlist
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://192.168.1.27:8000"

parser = argparse.ArgumentParser()
parser.add_argument('numbers',
                    nargs="+",
                    type=int,
                    help="Channel number to start at, or a list of individual channel numbers.")
parser.add_argument('-t',
                    '--thru',
                    type=int,
                    default=None,
                    help="Channel number to end at.")
args = parser.parse_args()

dtv = API(url=DIZQUETV_URL)

channel_numbers = []
if args.thru:
    if len(args.numbers) > 1:
        print("Please provide only one start number if you are using --thru.")
        exit(1)
    else:
        for num in range(args.numbers[0], args.thru + 1):
            channel_numbers.append(num)
else:
    channel_numbers = args.numbers

for number in channel_numbers:
    if number in dtv.channel_numbers:
        print(f"Channel {number} already exists. Not going to overwrite it.")
    else:
        channel = dtv.add_channel(programs=[],
                                  number=number,
                                  handle_errors=True)
        if channel:
            print(f"Created {channel.name} on dizqueTV.")
        else:
            print(f"Could not create channel {number} on dizqueTV.")