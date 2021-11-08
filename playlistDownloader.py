import configparser
import sys

config = configparser.ConfigParser()
if (not config.read('config.ini')):
    print("Configuration not done. :(")
    print("Please copy config.ini.sample into config.ini, and provide your client ID & secret.")
    print("Go here developer.spotify.com/dashboard/applications/ and set up an app")
    print("Don't forget to 'Edit Settings' and add a redirect URI for 'http://localhost:8888/callback'")
    sys.exit()

import os, csv
from datetime import datetime

os.environ["SPOTIPY_CLIENT_ID"] = config['DEFAULT']['SPOTIPY_CLIENT_ID']
os.environ["SPOTIPY_CLIENT_SECRET"] = config['DEFAULT']['SPOTIPY_CLIENT_SECRET']
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888/callback"

import unicodedata
import re

# shows a user's playlists (need to be authenticated via oauth)

import spotipy
import spotipy.util as util

startTime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

def makePathExist(folderPath):
    not os.path.exists(folderPath) and os.mkdir(folderPath)

def show_tracks(tracks, playlist_csv_writer):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        try:
            isrc_id = ''
            if 'external_ids' in track and 'isrc' in track['external_ids']:
                isrc_id = track['external_ids']['isrc']
            playlist_csv_writer.writerow([
                track['artists'][0]['name'], track['name'], 
                track['duration_ms'], track['id'], track['artists'][0]['id'],
                isrc_id
            ])
        except:
            print("Error copying track!")
            print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))
            raise

def show_playlist(playlist):
    if playlist['owner']['id'] == username:
        print()
        print(playlist['name'])
        print ('  total tracks', playlist['tracks']['total'])
        results = sp.playlist(playlist['id'],
            fields="tracks,next")
        tracks = results['tracks']

        makePathExist('playlists')
        makePathExist('playlists/' + startTime)

        playlist_file = open('playlists/' + startTime + '/' + slugify(playlist['name']) + '.csv', mode='w', encoding="utf-8", newline='')
        playlist_csv_writer = csv.writer(playlist_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        playlist_csv_writer.writerow(['Artist', 'Title', 'Duration', 'Spotify ID', 'Artist Spotify ID', 'ISRC_ID'])

        show_tracks(tracks, playlist_csv_writer)
        while tracks['next']:
            tracks = sp.next(tracks)
            show_tracks(tracks, playlist_csv_writer)
        playlist_file.close()

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Whoops, need your username!")
        print("Get it from here: https://www.spotify.com/ca-en/account/overview/")
        print("usage: python user_playlists.py [username]")
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                show_playlist(playlist)
    else:
        print("Can't get token for", username)