# main.py

from src.api_clients.spotify_api_client import SpotifyAPIClient

def main():
    client = SpotifyAPIClient()
    other_genres = client.get_all_genres_from_csv('data/spotify_data/all_unique_other_artists_sorted.csv')
    rock_genres = client.get_all_genres_from_csv('data/spotify_data/all_unique_rock_artists_sorted.csv')
    sourced_genres = client.load_from_text('data/spotify_data/genre_data/cleaned_genres_list.txt')
    
    rock_or_other_not_in_sourced = (rock_genres | other_genres) - sourced_genres
    print(f"Genres in 'rock' or 'other' but not in 'sourced': {len(rock_or_other_not_in_sourced)}")
    # print(rock_or_other_not_in_sourced)
    
    # Combine all genres into a final set
    final_genres = sourced_genres.union(other_genres).union(rock_genres)
    
    # Save the combined genre list to a new text file
    client.save_to_text(final_genres, 'data/spotify_data/genre_data/final_genre_list.txt')
    print(f"Final combined genre list saved with {len(final_genres)} unique genres.")
    # now list the genres in other, rock that are not in sourced, and how many are not in there
    # write the full genre list (combined) to a new txt final_genre_list.txt

    # client.process_and_save_multiple_genres(genres=genres, description="all")

if __name__ == "__main__":
    main()