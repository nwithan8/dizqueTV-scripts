from typing import List, Union

from plexapi import server, media, library, playlist, myplex
from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"
DIZQUETV_CHANNEL_NUMBER = 1
# Plex playlist will have the same name as the dizqueTV channel

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "thisisaplextoken"


class Plex:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.server = server.PlexServer(url, token)

    def get_users(self) -> List[myplex.MyPlexUser]:
        return self.server.myPlexAccount().users()

    def user_has_server_access(self, user) -> bool:
        for s in user.servers:
            if s.name == self.server.friendlyName:
                return True
        return False

    def get_playlists(self) -> List[playlist.Playlist]:
        return self.server.playlists()

    def get_playlist(self, playlist_name: str) -> Union[playlist.Playlist, None]:
        for playlist in self.get_playlists():
            if playlist.title == playlist_name:
                return playlist
        return None

    def create_new_playlist(self, playlist_name, items: List[media.Media]):
        self.server.createPlaylist(title=playlist_name, items=items)

    def reset_playlist(self, playlist_name, items: List[media.Media]):
        playlist = self.get_playlist(playlist_name=playlist_name)
        if playlist:
            playlist.delete()
        self.create_new_playlist(playlist_name=playlist_name, items=items)

    def get_library_sections(self) -> List[library.LibrarySection]:
        return self.server.library.sections()

    def get_all_section_items(self, section) -> List[media.Media]:
        return section.all()

    def get_plex_item(self, item, section_name=None) -> Union[media.Media, None]:
        if section_name:
            results = self.server.library.section(section_name).search(title=item.title)
        else:
            results = self.server.library.search(title=item.title)
        for media in results:
            if int(media.ratingKey) == int(item.ratingKey):
                return media
        return None


dtv = API(url=DIZQUETV_URL)
plex = Plex(url=PLEX_URL, token=PLEX_TOKEN)
channel = dtv.get_channel(channel_number=DIZQUETV_CHANNEL_NUMBER)
to_add = []
for program in channel.programs:
    plex_item = plex.get_plex_item(item=program)
    if plex_item:
        print(f"Adding {plex_item.title}...")
        to_add.append(plex_item)
plex.reset_playlist(playlist_name=channel.name, items=to_add)
