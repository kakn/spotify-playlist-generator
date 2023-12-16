import re

# Example artist and track names
artist_name = "Tyga feat. Offset"
song_title = "Taste feat. Offset"

# Regular expression pattern to match variations of "feat."
feat_pattern = re.compile(r"\b(feat\.?|ft\.?|featuring)\b", re.IGNORECASE)

# Remove "feat." variations from artist name and track title
clean_artist_name = re.sub(feat_pattern, "", artist_name).strip()
clean_song_title = re.sub(feat_pattern, "", song_title).strip()

# Extract featured artists (if any) and store in a list
featured_artists = [name.strip() for name in re.findall(feat_pattern, artist_name + " " + song_title)]

print(clean_artist_name)      # Output: Tyga
print(clean_song_title)       # Output: Taste
print(featured_artists)       # Output: ['Offset']

# Should probably now write to a new CSV

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

def find_track_on_spotify(song_title, artist_name):
    """Searches for a track on Spotify by song title and artist name, with support for featured artists."""

    # Initialize Spotify API client with credentials
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Regular expression pattern to match variations of "feat."
    feat_pattern = re.compile(r"\b(feat\.?|ft\.?|featuring)\b", re.IGNORECASE)

    # First try searching for track by song title and artist name
    query = f"{song_title} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)

    # If no results are found, try searching again with featured artists included in the query
    if not results['tracks']['items']:
        # Extract featured artists (if any) and add them to the search query
        featured_artists = [name.strip() for name in re.findall(feat_pattern, artist_name + " " + song_title)]
        if featured_artists:
            query += f" {featured_artists[0]}"
        results = sp.search(q=query, type='track', limit=1)

    # If a result is found, return its Spotify URI
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        return track_uri

    # If no results are found, return None
    return None
