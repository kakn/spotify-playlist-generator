import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

def find_track_on_spotify(song_title):
    # setting up Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id='68638f90ae504fc7b4e57953c72bf302',
                                                          client_secret='0c25a7ea73f2472986dde61c27fc1f57')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # split song title into track and artist
    track_artist_split = song_title.split(' - ')
    track = track_artist_split[0] if len(track_artist_split) > 1 else song_title
    artist = track_artist_split[1] if len(track_artist_split) > 1 else None

    # search for the track
    result = sp.search(track, type='track', limit=50)

    # filter results by artist
    if artist:
        result['tracks']['items'] = [item for item in result['tracks']['items'] if any(artist.lower() in a['name'].lower() for a in item['artists'])]

    # if results are found, return the first result's name and artist
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        return f"Found on Spotify: {track['name']} by {track['artists'][0]['name']}"
    else:
        return None