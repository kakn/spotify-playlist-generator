import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

def get_seed_tracks(sp, video_title):
    search_results = sp.search(q=video_title, limit=5, type='track')['tracks']['items']
    if search_results:
        return [track['id'] for track in search_results]

    artist_name = video_title.split("-")[0]
    secondary_search_results = sp.search(q=artist_name, limit=5, type='track')['tracks']['items']
    if secondary_search_results:
        return [track['id'] for track in secondary_search_results]

    return []

def get_related_tracks(sp, seed_tracks, total_tracks=50):
    try:
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=total_tracks)
        return [track['id'] for track in recommendations['tracks']]
    except Exception as e:
        print(f"Error occurred while fetching related tracks: {str(e)}")
        return []

def create_spotify_playlists(json_file_path, spotify_user_id):
    # Create the SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=spotify_api_details['client_id'],
                            client_secret=spotify_api_details['client_secret'],
                            redirect_uri='http://localhost:8888/callback',
                            scope='playlist-modify-public ugc-image-upload')

    # Retrieve the access token
    token_info = sp_oauth.get_cached_token() 

    # Create the Spotify client object with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])  # Access the token from the dictionary

    # Read the JSON file
    with open(json_file_path, 'r') as file:
        playlists_data = json.load(file)

    for playlist_name, image_path in tqdm(playlists_data.items(), desc="Creating playlists"):
        # Create a new playlist
        playlist = sp.user_playlist_create(user=spotify_user_id, name=playlist_name, public=True)
        print(f"\nCreated playlist: {playlist_name}")

        # Upload cover image for the playlist
        with open(image_path, 'rb') as image_file:
            sp.playlist_upload_cover_image(playlist_id=playlist['id'], image_b64=image_file.read())
            print(f"Uploaded cover image for playlist: {playlist_name}")

        seed_tracks = get_seed_tracks(sp, playlist_name)
        if seed_tracks:
            track_ids = get_related_tracks(sp, seed_tracks)
            if track_ids:
                sp.playlist_add_items(playlist['id'], items=track_ids)
                print(f"Added {len(track_ids)} related tracks to playlist: {playlist_name}")

spotify_api_details = {
    'client_id': 'fb21bef25fe340b58a574fa10b131e69',
    'client_secret': '74cc3728bca94b1da59a46e187e277fe'
}
# Example usage
spotify_user_id = '31arlratseg6qebkm73qkaphphku'
json_file_path = 'artist_playlists/music_data.json'
create_spotify_playlists(json_file_path, spotify_user_id)
