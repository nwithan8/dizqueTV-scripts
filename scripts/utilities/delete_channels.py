"""
Mass-delete channels on dizqueTV
"""
from typing import List, Union
import argparse

from plexapi import server, playlist
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

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

print(f"The following channels will be deleted from dizqueTV:\n{', '.join(str(num) for num in channel_numbers)}")
answer = input("Are you sure? (Y/N) ")
if answer.lower()[0] != 'y':
    print("Cancelling...")
    exit(0)

for number in channel_numbers:
    if not dtv.delete_channel(channel_number=number):
        print(f"Could not delete channel {number} on dizqueTV.")
    else:
        print(f"Deleted channel {number} on dizqueTV.")
