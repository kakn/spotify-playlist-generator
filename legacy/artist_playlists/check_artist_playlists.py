import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

def playlist_exists(playlist_title):
    # Set up Spotify API client
    client_credentials_manager = SpotifyClientCredentials(
        client_id='===REDACTED===',
        client_secret='===REDACTED==='
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for playlists with the given title
    try:
        playlists = sp.search(q=playlist_title, type='playlist')
        # Iterate over found playlists to check for an exact match
        for playlist in playlists['playlists']['items']:
            if playlist['name'].lower() == playlist_title.lower():
                return True
        return False
    except Exception as e:
        print('An error occurred:', e)
        return False

def update_json_file(json_file_path):
    # Read the existing JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Iterate through the keys and check if the playlist exists on Spotify
    keys_to_remove = []
    for key in tqdm(data.keys(), desc="Checking playlists"):
        if playlist_exists(key):
            print(f'Removing "{key}" from JSON file - playlist found on Spotify.')
            keys_to_remove.append(key)

    # Remove the keys that do not have a playlist on Spotify
    for key in keys_to_remove:
        del data[key]

    # Save the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
json_file_path = 'artist_playlists/music_data.json'
update_json_file(json_file_path)
