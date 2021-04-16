#!/usr/bin/env pipenv-shebang
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from xml.etree import ElementTree


handler = RotatingFileHandler('/var/log/emby-playlists/dedup.log', maxBytes=1024 * 1024 * 5, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
formatter.converter = time.gmtime
handler.setFormatter(formatter)
log = logging.getLogger('dedup_playlists.py')
log.setLevel('INFO')
log.addHandler(handler)

try:
    default_path = Path.home() / 'Music' / 'emby_playlists'
    playlist_path = Path(os.getenv('EMBY_PLAYLIST_PATH')) if os.getenv('EMBY_PLAYLIST_PATH') else default_path

    for playlist_file in playlist_path.rglob('playlist.xml'):
        log.info(f'Deduping playlist {playlist_file}')
        playlist_tree = ElementTree.parse(playlist_file)
        playlist_root = playlist_tree.getroot()
        songs = []
        items_element = playlist_root.find('./PlaylistItems')
        starting_len = len(items_element)
        for item in list(items_element):
            song = item.find('Path').text
            log.debug(f'\t{song}')
            if song in songs:
                log.debug('\t\tRemoving duplicate')
                items_element.remove(item)
            else:
                log.debug('\t\tNot a duplicate')
                songs.append(song)
        playlist_tree.write(playlist_file, 'utf-8')
        ending_len = len(items_element)
        if starting_len != ending_len:
            log.info(f'\tRemoved {starting_len - ending_len} duplicates from the playlist')
        else:
            log.info('\tNo duplicates were found in the playlist')
except Exception:
    log.exception('Failed to dedup the playlists')
    raise
