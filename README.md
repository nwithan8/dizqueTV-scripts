# dizqueTV-scripts
Scripts to automate dizqueTV tasks

# Installation
1. Clone this repo with ``git clone https://github.com/nwithan8/dizqueTV-scripts.git``
2. Enter ``dizqueTV-scripts`` directory
3. Install dependencies with ``pip install -r requirements.txt``
4. Enter ``scripts`` folder
5. Run a script with ``python <script_name>``

All scripts are standalone, meaning (as long as dependencies are installed), any script can run regardless of where the file is located on your machine.


# Script descriptions
- ``channel_to_playlist.py``: Copy all items from a dizqueTV channel to a Plex playlist (make a new playlist if one doesn't exist).
- ``playlist_to_channel.py``: Copy all items from a Plex playlist to an existing dizqueTV channel.
- ``studio_channel``: Make a new channel with all content from a specific movie studio, TV network or streaming platform.