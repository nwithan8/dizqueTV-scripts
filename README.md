# dizqueTV-scripts
Scripts to automate dizqueTV tasks

# Installation
1. Clone this repo with `git clone https://github.com/nwithan8/dizqueTV-scripts.git`
1. Enter `dizqueTV-scripts` directory
1. Install dependencies with `pip install -r requirements.txt`
1. Run a script with `python <script_name>`

All scripts are standalone, meaning (as long as dependencies are installed) any script can run regardless of where the file is located on your machine.

Use `python <script_name> --help` to see the script's help message.

# Script descriptions
- [`channel_to_playlist.py`](scripts/basic/channel_to_playlist.py): Copy all items from a dizqueTV channel to a Plex playlist (make a new playlist if one doesn't exist).
- [`playlist_to_channel.py`](scripts/basic/playlist_to_channel.py): Copy all items from a Plex playlist to an existing dizqueTV channel.
- [`collection_to_channel.py`](scripts/basic/collection_to_channel.py): Copy all items from a Plex collection to an existing dizqueTV channel.
- [`make_blank_channels.py`](scripts/utilities/make_blank_channels.py): Create multiple "blank" channels on dizqueTV.
- [`delete_channels.py`](scripts/utilities/delete_channels.py): Delete multiple channels on dizqueTV.
- [`find_broken_links.py`](scripts/utilities/find_broken_links.py): Find broken media links in dizqueTV channels (content path that has changed or no longer exists).
- [`replace_old_url.py`](scripts/utilities/replace_old_url.py): Replace old URLs in dizqueTV channels with new URLs.
- [`trending_shows.py`](scripts/trending/trending_shows.py): Search for and add the top 10 trending shows (via Trakt) to a dizqueTV channel.
- [`trending_movies.py`](scripts/trending/trending_movies.py): Search for and add the top 10 trending movies (via Trakt) to a dizqueTV channel.
- [`studio_channel.py`](scripts/channel_by/studio_channel.py): Make a new channel with all content from specific movie studio, TV network or streaming platform(s).
- [`genre_channel.py`](scripts/channel_by/genre_channel.py): Make a new channel with all content from specific genre(s).
- [`keyword_channel.py`](scripts/channel_by/keyword_channel.py): Make a new channel with all content matching specific keyword(s).
