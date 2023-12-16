import spotipy
from spotipy.oauth2 import SpotifyOAuth

def delete_all_playlists(spotify_api_details):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_api_details['client_id'],
                                                   client_secret=spotify_api_details['client_secret'],
                                                   redirect_uri="http://localhost:8000",
                                                   scope='playlist-modify-public ugc-image-upload',
                                                   open_browser=False))

    playlists = sp.current_user_playlists(limit=50)  # Adjust the limit if you have more than 50 playlists

    for playlist in playlists['items']:
        sp.user_playlist_unfollow(playlist['owner']['id'], playlist['id'])
        print(f"Deleted playlist: {playlist['name']}")

spotify_api_details = {
    'client_id': '749cacc699c44f3ca7d3a9048f5cfb75',
    'client_secret': '9f2d3df22a774b21917a4d230ca5db3e'
}

delete_all_playlists(spotify_api_details)
