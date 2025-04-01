import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import time
import requests

# Spotify API credentials
client_id_rg = '749cacc699c44f3ca7d3a9048f5cfb75'
client_secret_rg = '9f2d3df22a774b21917a4d230ca5db3e'

client_id_kk = 'd45115664aa242c2bec6d1427dce642d'
client_secret_kk = '477c8ec1cd654c178c801fde3fc341aa'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id_rg, client_secret=client_secret_rg)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=30, retries=10, status_retries=10, backoff_factor=0.2)

user_id_rg = '31ecqbn3cnpznklsi6k5htlvhc5q'
user_id_kk = '11167946888'

def get_user_playlists(spotify_client, user):
    try:
        return spotify_client.user_playlists(user)
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get('Retry-After', 0))
            print(f"Rate limit exceeded, sleeping for {retry_after} seconds")
            time.sleep(retry_after)
            return get_user_playlists(spotify_client, user)
        raise

# Robust request function
def robust_request(func, *args):
    for i in range(10):  # Adjust the range as needed
        try:
            return func(*args)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error ({e}), retrying in 5 seconds...")
            time.sleep(5)  # Adjust the sleep duration as needed
    raise RuntimeError("Failed to connect after multiple attempts")

# Initialize playlist results
playlists = get_user_playlists(sp, user_id_rg)
total_playlists = playlists['total']  # Get total number of playlists
total_followers = 0

pbar = tqdm(total=total_playlists)  # Initialize progress bar

while playlists:
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user_id_rg:
            # Fetch full playlist object to get 'followers' field
            full_playlist = None
            while full_playlist is None:
                try:
                    full_playlist = robust_request(sp.playlist, playlist['id'])
                except spotipy.exceptions.SpotifyException as e:
                    if e.http_status == 429:
                        retry_after = int(e.headers.get('Retry-After', 0))
                        print(f"Rate limit exceeded, sleeping for {retry_after} seconds")
                        time.sleep(retry_after)
            followers = full_playlist['followers']['total']
            if followers > 0:
                print(f"Playlist '{full_playlist['name']}' has {followers} follower(s)")
                total_followers += followers
        pbar.update(1)  # Update progress bar
    # if there are more playlists, get the next set
    while True:
        try:
            if 'next' in playlists and playlists['next']:
                playlists = robust_request(sp.next, playlists)
            else:
                playlists = None
            break
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get('Retry-After', 0))
                print(f"Rate limit exceeded, sleeping for {retry_after} seconds")
                time.sleep(retry_after)

pbar.close()  # Close progress bar

print(f"\nTotal followers across all playlists: {total_followers}")
