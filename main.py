# main.py

from src.api_clients.spotify_api_client import SpotifyAPIClient

def main():
    client = SpotifyAPIClient()
    client.find_unreleased_playlists('data/spotify_data/all_unique_artists_sorted.csv', 
                                     'data/spotify_data/processed_artists.csv')

if __name__ == "__main__":
    main()