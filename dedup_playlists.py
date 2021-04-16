#!/usr/bin/env pipenv-shebang
import os
from pathlib import Path
from xml.etree import ElementTree

default_path = Path.home() / 'Music' / 'emby_playlists'
playlist_path = Path(os.getenv('EMBY_PLAYLIST_PATH')) if os.getenv('EMBY_PLAYLIST_PATH') else default_path

for playlist_file in playlist_path.rglob('playlist.xml'):
    playlist_tree = ElementTree.parse(playlist_file)
    playlist_root = playlist_tree.getroot()
    songs = []
    items_element = playlist_root.find('./PlaylistItems')
    for item in list(items_element):
        song = item.find('Path').text
        if song in songs:
            items_element.remove(item)
        else:
            songs.append(song)
    playlist_tree.write(playlist_file, 'utf-8')
