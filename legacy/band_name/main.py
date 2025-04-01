### This file is used for testing modules
from check_artist import *

def main():
    # Fetch the Spotify access token
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
    
    response = check_single_artist_on_spotify("noreaster", token)
    
    if response:
        print("'noreaster' exists on Spotify.")
    else:
        print("'noreaster' does not exist on Spotify.")

if __name__ == "__main__":
    main()
