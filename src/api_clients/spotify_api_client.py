import ast
import os
import re
from typing import Any, Dict, List, Tuple, Set

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

from src.api_clients.abstract_api_client import AbstractAPIClient

class SpotifyAPIClient(AbstractAPIClient):

    MAX_LIMIT = 1000

    def __init__(self):
        super().__init__('SPOTIFY')
        self.clients = [self._create_spotify_client(key) for key in self.api_keys]

    def _process_api_key(self, key: str) -> Tuple[str, str]:
        client_id, client_secret = key.split(':')
        return client_id, client_secret

    @staticmethod
    def _create_spotify_client(key: Tuple[str, str]) -> spotipy.Spotify:
        client_id, client_secret = key
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def _should_rotate(self, exception: Exception) -> bool:
        return isinstance(exception, spotipy.SpotifyException) and exception.http_status == 429

    def _get_current_key(self) -> spotipy.Spotify:
        return self.clients[self.current_key_index]

    @staticmethod
    def combine_csv_files(folder_path: str, output_file: str) -> None:
        """
        Combines all CSV files in the specified folder, keeping unique entries based on 'id',
        aggregating genres, and sorting by popularity and followers.
        """
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        combined_df = pd.concat([pd.read_csv(os.path.join(folder_path, f)) for f in csv_files], ignore_index=True)
        combined_df['genres'] = combined_df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        genre_aggregation = combined_df.groupby('id')['genres'].agg(lambda x: list(set(genre for genres in x for genre in genres)))
        
        combined_df = (combined_df.drop_duplicates(subset='id', keep='first')
                                  .set_index('id')
                                  .assign(genres=genre_aggregation)
                                  .reset_index()
                                  .sort_values(['popularity', 'followers'], ascending=[False, False]))

        column_order = ['name', 'popularity', 'followers', 'genres', 'id', 'spotify_url', 'images']
        combined_df = combined_df[column_order]
        combined_df['genres'] = combined_df['genres'].astype(str)

        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV saved to {output_file}")
        print(f"Total unique artists: {len(combined_df)}")

    def get_artist_genres(self, artist_names: List[str]) -> Dict[str, List[str]]:
        artist_genres = {}
        for name in tqdm(artist_names, desc="Fetching Artist Genres"):
            results = self.clients[0].search(q=name, type='artist', limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                artist_genres[name] = artist['genres']
            else:
                artist_genres[name] = []
        return artist_genres

    def get_top_artists_by_genre(self, genre: str, limit: int = 1000) -> List[Dict[str, Any]]:
        def _get_artists_page(client: spotipy.Spotify, genre: str, limit: int, offset: int = 0) -> Dict[str, Any]:
            results = client.search(q=f'genre:"{genre}"', type='artist', limit=limit, offset=offset)
            artists = results['artists']
            
            artists['items'] = [
                {
                    'name': artist['name'],
                    'popularity': artist['popularity'],
                    'followers': artist['followers']['total'],
                    'genres': artist['genres'],
                    'id': artist['id'],
                    'spotify_url': artist['external_urls']['spotify'],
                    'images': [img['url'] for img in artist['images']] if artist['images'] else []
                }
                for artist in artists['items']
            ]
            
            return artists
        
        if limit > self.MAX_LIMIT:
            print(f"Warning: Spotify's API limits the number of search results. Max fetch limit is {self.MAX_LIMIT}.")
            limit = self.MAX_LIMIT

        all_artists = self.paginate(_get_artists_page, genre=genre, total=limit)
        sorted_artists = sorted(all_artists, key=lambda x: (x['popularity'], x['followers']), reverse=True)
        return sorted_artists
    
    @staticmethod
    def normalize_genre_name(genre: str) -> str:
        genre = genre.lower()
        genre = genre.replace(' ', '_')
        genre = re.sub(r'[^\w\-]', '', genre)
        return genre

    def process_artists_and_save_top_genres(self, artists: List[str], description: str) -> None:
        genres = self.get_artist_genres(artists)
        for artist, gs in genres.items():
            print(f"{artist}: {gs}")
        
        unique_genres = {g for gs in genres.values() for g in gs}
        self.process_and_save_multiple_genres(unique_genres, description)

    def process_and_save_multiple_genres(self, genres: Set[str], description: str) -> None:
        parent_dir = f"data/spotify_data/top_{description}_artists_per_genre"
        os.makedirs(parent_dir, exist_ok=True)
        
        for idx, genre in enumerate(genres, 1):
            normalized = self.normalize_genre_name(genre)
            filepath = os.path.join(parent_dir, f"top_{normalized}_artists.csv")
            
            if os.path.exists(filepath):
                print(f"Skipping genre {idx}/{len(genres)}: {genre} (CSV already exists)")
                continue
            
            print(f"Processing genre {idx}/{len(genres)}: {genre}")
            
            top_artists = self.get_top_artists_by_genre(genre)
            self.save_to_csv(top_artists, filepath)

    def get_related_genres(self, genre: str) -> Set[str]:
        recommendations = self._get_current_key().recommendations(seed_genres=[genre])
        related_genres = set()
        for track in recommendations['tracks']:
            for artist in track['artists']:
                artist_info = self._get_current_key().artist(artist['id'])
                related_genres.update(artist_info['genres'])
        return related_genres - {genre}

    def collect_all_genres(self, seed_genres: List[str]) -> Set[str]:
        all_genres, genres_to_check, checked_genres = self.load_genre_progress()
        
        if not all_genres:
            all_genres = set(seed_genres)
            genres_to_check = set(seed_genres)

        with tqdm(desc="Collecting genres") as pbar:
            while genres_to_check:
                current_genre = genres_to_check.pop()
                if current_genre not in checked_genres:
                    related_genres = self.get_related_genres(current_genre)
                    new_genres = related_genres - all_genres
                    all_genres.update(new_genres)
                    genres_to_check.update(new_genres)
                    checked_genres.add(current_genre)
                    pbar.update(1)
                    pbar.set_postfix({"Total": len(all_genres), "To Check": len(genres_to_check)})
                
                self.save_genre_progress(all_genres, genres_to_check, checked_genres)

        return all_genres

    def save_genre_progress(self, all_genres: Set[str], genres_to_check: Set[str], checked_genres: Set[str]):
        self.save_to_text(all_genres, 'data/spotify_data/genre_data/all_genres.txt')
        self.save_to_text(genres_to_check, 'data/spotify_data/genre_data/genres_to_check.txt')
        self.save_to_text(checked_genres, 'data/spotify_data/genre_data/checked_genres.txt')

    def load_genre_progress(self) -> Tuple[Set[str], Set[str], Set[str]]:
        all_genres = self.load_from_text('data/spotify_data/genre_data/all_genres.txt')
        genres_to_check = self.load_from_text('data/spotify_data/genre_data/genres_to_check.txt')
        checked_genres = self.load_from_text('data/spotify_data/genre_data/checked_genres.txt')
        return all_genres, genres_to_check, checked_genres

    @staticmethod
    def get_all_genres_from_csv(csv_file: str) -> Set[str]:
        df = pd.read_csv(csv_file)
        all_genres = set()
        for genres_str in df['genres']:
            genres = ast.literal_eval(genres_str)
            all_genres.update(genres)
        return all_genres