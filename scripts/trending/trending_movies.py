"""
Add the top 10 trending movies to a channel on dizqueTV
Refreshes the channel (removes all existing programs, re-adds new items)
"""

from typing import List, Union
import argparse

import requests
from plexapi import server, video
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"

# Make a Trakt application: https://trakt.tv/oauth/applications
# Use redirect URI: urn:ietf:wg:oauth:2.0:oob
TRAKT_CLIENT_ID = "traktclientid"
TRAKT_CLIENT_SECRET = "traktclientsecret"


parser = argparse.ArgumentParser()
parser.add_argument('-n',
                    '--channel_name',
                    type=str,
                    default="Trending Movies",
                    help="Name of channel to create/edit")
parser.add_argument('-c', '--channel_number',
                    nargs='?',
                    type=int,
                    default=None,
                    help="dizqueTV channel to add playlist to.")
args = parser.parse_args()

class TraktConnection:
    def __init__(self):
        pass

    def request(self, endpoint: str) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': TRAKT_CLIENT_ID,
            'x-pagination-page': '1',
            'x-pagination-limit': '20'
        }
        res = requests.get(f'https://api.trakt.tv{endpoint}', headers=headers)
        if res:
            return res.json()
        return {}

    def get_trending_movies(self):
        data = self.request(endpoint='/movies/trending')
        items = []
        for entry in data:
            items.append(entry.get('movie'))
        return items

    def get_trending_shows(self):
        data = self.request(endpoint='/shows/trending')
        items = []
        for entry in data:
            items.append(entry.get('show'))
        return items


class Plex:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.server = server.PlexServer(url, token)

    def get_plex_movie(self, movie_name: str, year: int = None, section_name = None) -> Union[video.Movie, None]:
        search_kwargs = {
            'title': movie_name
        }
        if year:
            search_kwargs['year'] = year
        if section_name:
            results = self.server.library.section(section_name).search(**search_kwargs)
        else:
            results = self.server.library.search(**search_kwargs)
        for result in results:
            if type(result) == video.Movie and result.title == movie_name:
                return result
        return None

dtv = API(url=DIZQUETV_URL)
plex = Plex(url=PLEX_URL,
            token=PLEX_TOKEN)
trakt = TraktConnection()

this_channel = None
# try to get channel by number first
if args.channel_number:
    this_channel = dtv.get_channel(channel_number=args.channel_number)
# if failed, get channel by name
if not this_channel:
    for channel in dtv.channels:
        if channel.name == args.channel_name:
            this_channel = channel
# if still failed, make new channel (try with number, but handle error if can't)
if this_channel:
    print(f"Found and using {this_channel.name} on dizqueTV. This channel will be reset.")
if not this_channel:
    if not args.channel_number:
        args.channel_number = max(dtv.channel_numbers) + 1
    print(f"Could not find that channel. Creating it on dizqueTV...")
    this_channel = dtv.add_channel(name=args.channel_name, programs=[], number=args.channel_number, handle_errors=True)
# if still no channel, exit
if not this_channel:
    print("Could not create that channel. Exiting...")
    exit(1)

movies_to_add = []
trending_movies = trakt.get_trending_movies()
for trakt_movie in trending_movies:
    print(f"Searching for {trakt_movie.get('title')} on Plex...")
    matching_plex_movie = plex.get_plex_movie(movie_name=trakt_movie.get('title'), year=trakt_movie.get('year'))
    if not matching_plex_movie:
        print(f"Could not find {trakt_movie.get('title')} on Plex.")
    else:
        print(f"Found {matching_plex_movie.title} on Plex. Adding to dizqueTV...")
        dizquetv_movie = dtv.convert_plex_item_to_program(plex_item=matching_plex_movie, plex_server=plex.server)
        if dizquetv_movie:
            movies_to_add.append(dizquetv_movie)

if this_channel.delete_all_programs():
    if this_channel.add_programs(programs=movies_to_add):
        print("Complete!")
