"""
Requires dizqueTV 1.3.0.0+

Replace old image URLs with a new one.
Use if your Plex server's IP address has changed.

IMPORTANT:
    If your Plex server's IP address has changed (dizqueTV can no longer connect),
    DO NOT delete your Plex server and re-add it. You will have to recreate all your channels.

    Instead, in dizqueTV, go to Settings -> Plex -> Sign in/Add Servers.
    Log in to your Plex account. This will import duplicates of all your Plex servers.
    Locate the new entry from your server (should be SERVER_NAME2), and click the edit icon next to it.
    Copy the Server URI and the User Access Token (select the eye icon to see it) then hit close.
    Locate the original entry for your server (SERVER_NAME) and click the edit icon next to it.
    Replace the Server URI and User Access Token with the ones you just copied. Click Save.
    dizqueTV will now use the new credentials when grabbing the media files from your server, without you
    having to replace your channels.
    Delete all duplicate Plex Server entries if you'd like.

    The Plex credentials are only used when interacting with media items from your server.
    Icons, episode thumbnails, posters, etc. will still use the old server URI.
    That's what this script will fix.
"""

import argparse
from progress.bar import Bar

from dizqueTV import API

# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"

parser = argparse.ArgumentParser()
parser.add_argument('old_url',
                    type=str,
                    help="Old URL (or partial URL) to replace with the new URL")
parser.add_argument('new_url',
                    type=str,
                    help="New URL (or partial URL) to replace the old URL")
parser.add_argument("-v",
                    "--verbose",
                    action="store_true",
                    help="Verbose (for debugging)")
args = parser.parse_args()


dtv = API(url=DIZQUETV_URL, verbose=args.verbose)

print(f"Will replace {args.old_url} with {args.new_url} on all programs and filler items.")

for channel in dtv.channels:
    """
    DOES NOT UPDATE THE FALLBACK ITEM
    for filler_item in channel.fallback:
        new_data = {'icon': filler_item.icon.replace(args.old_url, args.new_url)}
        if filler_item.type == "episode":
            new_data['episodeIcon'] = filler_item.episodeIcon.replace(args.old_url, args.new_url)
            new_data['seasonIcon'] = filler_item.seasonIcon.replace(args.old_url, args.new_url)
            new_data['showIcon'] = filler_item.showIcon.replace(args.old_url, args.new_url)
        filler_item.update(**new_data)
    """
    print(f"Gathering programs on channel {channel.number}...")
    programs = channel.programs
    with Bar(f"Updating content on channel {channel.number}", max=len(programs)) as bar:
        for program in programs:
            new_data = {'icon': program.icon.replace(args.old_url, args.new_url)}
            if program.type == "episode":
                new_data['episodeIcon'] = program.episodeIcon.replace(args.old_url, args.new_url)
                new_data['seasonIcon'] = program.seasonIcon.replace(args.old_url, args.new_url)
                new_data['showIcon'] = program.showIcon.replace(args.old_url, args.new_url)
            program.update(**new_data)
            bar.next()
        bar.finish()

for filler_list in dtv.filler_lists:
    print(f"Gathering filler items on Filler List {filler_list.name}...")
    filler_items = filler_list.content
    with Bar(f"Updating filler items on Filler List {filler_list.name}", max=len(filler_items)) as bar:
        for filler_item in filler_list.content:
            new_data = {'icon': filler_item.icon.replace(args.old_url, args.new_url)}
            if filler_item.type == "episode":
                new_data['episodeIcon'] = filler_item.episodeIcon.replace(args.old_url, args.new_url)
                new_data['seasonIcon'] = filler_item.seasonIcon.replace(args.old_url, args.new_url)
                new_data['showIcon'] = filler_item.showIcon.replace(args.old_url, args.new_url)
            filler_item.update(**new_data)
            bar.next()
        bar.finish()

print("Completed.")
