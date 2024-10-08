import ast
import os
import re
from typing import Any, Dict, List, Set, Tuple

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
from unidecode import unidecode

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

    def find_unreleased_playlists(self, input_csv: str, output_csv: str) -> None:
        """
        Reads artists from input_csv, adds an 'alias' column using unidecode,
        searches for playlists titled "unreleased [artist name]" or "unreleased [alias]",
        and writes to output_csv with added columns for the count of such playlists and their IDs.
        """
        if os.path.exists(output_csv):
            processed_df = pd.read_csv(output_csv)
            processed_artists = set(processed_df['id'])
            mode = 'a'  # Append mode
            header = False
        else:
            processed_df = pd.DataFrame()
            processed_artists = set()
            mode = 'w'  # Write mode
            header = True

        df = pd.read_csv(input_csv)
        df = df[df['followers'] >= 100000]
        df.insert(1, 'alias', df['name'].apply(
            lambda x: unidecode(x) if unidecode(x).lower() != x.lower() else ''
        ))
        total_artists = len(df)
        skipped_artists = []

        output_columns = df.columns.tolist()
        output_columns.insert(2, 'unreleased_playlists_count')
        output_columns.append('unreleased_playlists_ids')

        with open(output_csv, mode, newline='', encoding='utf-8') as f_out:
            pbar = tqdm(total=total_artists, initial=len(processed_artists), desc="Processing Artists")

            for _, row in df.iterrows():
                artist_id = row['id']
                artist_name = row['name']
                alias = row['alias']

                if artist_id in processed_artists:
                    pbar.update(1)
                    continue

                try:
                    count, playlist_ids = self._count_playlists_with_terms_in_title(artist_name, alias)
                    row_data = row.tolist()
                    row_data.insert(2, count)
                    row_data.append(str(playlist_ids))
                    pd.DataFrame([row_data], columns=output_columns).to_csv(f_out, header=header, index=False)
                    header = False

                except Exception as e:
                    if self._should_rotate(e):
                        self._rotate_api_key()
                        continue
                    else:
                        skipped_artists.append(artist_name)
                finally:
                    processed_artists.add(artist_id)
                    pbar.update(1)

            pbar.close()

            if skipped_artists:
                print(f"Skipped artists due to errors: {skipped_artists}")

    def _count_playlists_with_terms_in_title(self, artist_name: str, alias: str) -> Tuple[int, List[str]]:
        """
        Searches for playlists containing 'unreleased' and the artist's name or alias as whole words (case-insensitive),
        and returns the count and list of unique playlist IDs that match the criteria.
        """
        limit = 50  # Number of playlists to fetch per request
        max_offset = 10000  # Spotify API maximum offset limit
        playlist_ids = set()
        queries = [f'unreleased {artist_name}']
        if alias and alias.lower() != artist_name.lower():
            queries.append(f'unreleased {alias}')

        for query in queries:
            offset = 0
            while offset < max_offset:
                response = self._get_current_key().search(q=query, type='playlist', limit=limit, offset=offset)
                playlists = response['playlists']['items']

                if not playlists:
                    break

                for playlist in playlists:
                    playlist_name = playlist['name'].lower()
                    if (re.search(r'\bunreleased\b', playlist_name) and
                        (re.search(rf'\b{re.escape(artist_name.lower())}\b', playlist_name) or
                        (alias and re.search(rf'\b{re.escape(alias.lower())}\b', playlist_name)))):
                        playlist_ids.add(playlist['id'])

                if len(playlists) < limit:
                    break  # Reached the end of results

                offset += limit

        total_exact_matches = len(playlist_ids)
        playlist_ids = list(playlist_ids)

        return total_exact_matches, playlist_ids

    @staticmethod
    def sort_csv_by_followers(input_csv: str) -> None:
        """
        Reads the CSV file, swaps 'followers' and 'popularity' columns, 
        sorts the DataFrame by the 'followers' column in descending order,
        and writes the sorted DataFrame to a new CSV file.
        """
        df = pd.read_csv(input_csv)

        cols = df.columns.tolist()
        idx_popularity = cols.index('popularity')
        idx_followers = cols.index('followers')

        cols[idx_followers], cols[idx_popularity] = cols[idx_popularity], cols[idx_followers]
        df = df[cols]

        df_sorted = df.sort_values(by='followers', ascending=False)
        df_sorted.to_csv(input_csv, index=False)
        print(f"Sorted CSV saved to {input_csv}")

    @staticmethod
    def get_non_alphanumeric_names(csv_file: str) -> List[str]:
        """
        Reads the CSV file and returns a list of names that contain non-alphanumeric characters
        for artists with 100,000 or more followers, maintaining the original order of the CSV.

        Args:
            csv_file (str): Path to the CSV file.

        Returns:
            List[str]: A list of names containing non-alphanumeric characters, in original CSV order.
        """
        df = pd.read_csv(csv_file)
        
        def contains_non_alphanumeric(name: str) -> bool:
            return bool(re.search(r'[^a-zA-Z0-9\s]', name))

        # Filter for artists with 100,000 or more followers
        df_filtered = df[df['followers'] >= 100000]

        # Create a boolean mask for non-alphanumeric names
        non_alphanumeric_mask = df_filtered['name'].apply(contains_non_alphanumeric)

        # Apply the mask and get the names, maintaining the original order
        non_alphanumeric_names = df_filtered.loc[non_alphanumeric_mask, 'name'].tolist()

        return non_alphanumeric_names