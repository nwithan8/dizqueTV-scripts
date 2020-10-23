"""
Make "blank" channels on dizqueTV
Each channel will have a single default Flex time.
"""

from typing import List, Union
import argparse

from plexapi import server, playlist
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

parser = argparse.ArgumentParser()
parser.add_argument('start_number',
                    type=int,
                    help="Channel number to start at.")
parser.add_argument('end_number',
                    type=int,
                    help="Channel number to end at.")
args = parser.parse_args()


dtv = API(url=DIZQUETV_URL)

for number in range(args.start_number, args.end_number + 1):
    channel = dtv.add_channel(programs=[],
                              number=number,
                              handle_errors=True)
    if channel:
        print(f"Created channel {number} on dizqueTV.")
    else:
        print(f"Could not create channel {number} on dizqueTV.")
