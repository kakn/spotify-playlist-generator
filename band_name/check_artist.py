import requests
from tqdm import tqdm
import time
import base64

CLIENT_SECRET = '9556bff0ffc54cc0bbca64ef79cf93df'
CLIENT_ID = '3ea9f87d635f4d5fa8b509a7b626f08c'
MAX_RETRIES = 5  # You can adjust this as needed

def get_spotify_token(client_id, client_secret):
    try:
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('ascii')
            },
            data={
                'grant_type': 'client_credentials'
            }
        )
        auth_response_data = auth_response.json()
        return auth_response_data['access_token']
    except Exception as e:
        print(f"Error obtaining Spotify token: {e}")
        return None

def is_artist_on_spotify(artist_name, token):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            headers = {
                'Authorization': 'Bearer ' + token
            }
            query = 'https://api.spotify.com/v1/search?q=' + artist_name + '&type=artist'
            response = requests.get(query, headers=headers, timeout=30)  # 30-second timeout
            artist_data = response.json()

            if 'artists' not in artist_data:
                print(f"Unexpected response from Spotify for artist '{artist_name}': {artist_data}")  # Print the unexpected response
                raise ValueError(f"Unexpected response format: {artist_data}")
            
            for artist in artist_data['artists']['items']:
                if artist['name'].lower() == artist_name.lower():  # case-insensitive comparison
                    return True

            return False
        except Exception as e:
            print(f"Error checking artist on Spotify: {e}. Retrying...")
            retries += 1
            time.sleep(2 ** retries)  # Exponential backoff

    # If we've retried MAX_RETRIES times and still have an error, 
    # consider the name as unchecked and write it to a separate file.
    with open('band_name/data/unchecked_names.txt', 'a') as unchecked_file:
        unchecked_file.write(artist_name + '\n')

    return False

def check_artists_in_file(file_path):
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
    if not token:
        print("Couldn't get Spotify token.")
        return

    with open(file_path, 'r') as file, open('band_name/data/er_available_names.txt', 'a') as output_file:
        lines = file.readlines()
        for line in tqdm(lines, desc="Checking names", unit="name"):
            artist_name = line.strip()
            if not is_artist_on_spotify(artist_name, token):
                output_file.write(artist_name + '\n')
                output_file.flush()  # Write to the file in real-time

def main(filepath):
    check_artists_in_file(filepath)

if __name__ == "__main__":
    main("band_name/data/er_generated_words.txt")