# Spotify Playlist Generator
This project aims at auto-generating Spotify playlists that are expected to gain followers. Much of the code is still messy and should be generalized to work in a pipeline (so it can be run all day).

## Order of operations
The order in which the files are run are as follows:
* 1 - yt_playlist_scraper.py
    * This file uses one Google API key to harvest playlist id's, given a key phrase such as 'not on spotify' or 'unreleased'. These ID's are saved in "playlist_ids.txt".
* 2 - yt_playlist_parser.py
    * This file rotates five Google API keys to parse the playlist ID list and collects the metadata of the videos. This metadata is saved in as dictionary objects within "youtube_videos.json". 
* 3 - preprocess_yt_videos.py
    * This file reads the JSON file and extracts relevant metadata. This relevant metadata includes 'Artist', 'Song Title', 'Video ID', 'View Count' and 'Thumbnail URL'. This file also defines a method to separate the artist name and song title from the video title using OpenAI, although this method is inconsistent. 
* 4 - sp_check_playlist_exists.py
    * This file reads the JSON file and extracts relevant metadata. This relevant metadata includes 'Video Title', 'Video ID', 'View Count' and 'Thumbnail URL'. It is checked whether a playlist of the video title exists, minimizing the pool of potential playlists. These videos are saved in "potential_playlists.csv", and will be further minimized.
* 5 - sp_check_song_exists.py
    * From here, the "potential_playlists.csv" can be further minimized by checking whether the playlist names exist as songs on Spotify. The potential follower gain of this project comes from songs not being available on Spotify, so it would make no sense to create a playlist of a song if the real song was available. There are two methods to this strategy:
        * Regex method - The title is stripped of square and circular brackets, and any keywords such as "Official", "Lyrics" "Music Video" etc. From here, the artist name and song name are collected, and passed to find_track_on_spotify(), returning None if the song is not found.
        * AI method - If the song is not found, the video title is passed to GPT 3.5-turbo, with a prompt asking for the artist name and song name to be separated. Regex then collects this information, and passes it to find_track_on_spotify(). 
    * If both methods return None, the playlist should be generated. Additionally, for both methods, the resulting artist name and song name is concatenated with a hyphen (" - "), and the existance of a playlist is checked. This is to double-check that a playlist of the song does not exist, with something like "[Official Music Video]" stripped from the title.
    

## Features to implement
* Search trending keywords on YouTube, Google, TikTok etc. to make playlists (memes, trending key words etc.). The idea is to be the first one to make a playlist with this name. The playlist could be filled with relevant TikTok songs.
* Descriptive tags in playlist description. Potentially, OpenAI could create tags based on the video title and video description. 
* 3 month free Spotify with PayPal
* gen_spotify_playlist.py
* Pipeline collecting all the Python files into one sequential main function.
* Strip leading and trailing quotation marks
* Find out how Spotify search API works - is it precise?
* Store number of playlist items