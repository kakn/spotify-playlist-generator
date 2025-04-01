import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import csv
import requests

def read_results():
    results = open('data/unreleased/youtube_videos_4.json')
    results_dict = json.load(results)
    results.close()
    return results_dict

def collect_data(results_dict):
    playlist_item_list = []
    for result in results_dict.items():
        dict_key = result[0]
        dict_items = results_dict[dict_key]
        data = dict_items[0]
        try:
            title = str(data['snippet']['title'])
            video_id = str(data['contentDetails']['videoId'])
            thumbnail_url = str(data['snippet']['thumbnails']['default']['url'])
            view_count = int(data['items'][0]['statistics']['viewCount'])
            playlist_item_list.append([title, video_id, view_count, thumbnail_url])
        except (KeyError, IndexError, UnicodeEncodeError):
            continue
    return playlist_item_list

def playlist_exists(playlist_title):
    # Set up Spotify API client
    client_credentials_manager = SpotifyClientCredentials(client_id='68638f90ae504fc7b4e57953c72bf302',
                                                          client_secret='0c25a7ea73f2472986dde61c27fc1f57')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    # Search for playlists with the given title
    try:
        playlists = sp.search(q=playlist_title, type='playlist')
        # Check if any playlists were found
        if playlists['playlists']['total'] > 0:
            return True
        else:
            return False
    except Exception as e:
        print('An error occurred:', e)
        playlist_exists(playlist_title)

def write_csv(items, filename):
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:
            writer.writerow(['Artist', 'Song Title', 'Video ID', 'View Count', 'Thumbnail URL'])
        c = 1
        d = 0
        for item in items: # if indexing, remember to -1 from c, unlike preproc.py
            print("Item {a} of {b} ({g}%)".format(a=c, b=len(items), g=round((c/len(items))*100, 2))) # implement percentages
            exists = playlist_exists(item[0])
            if not exists:
                writer.writerow(item)
                d += 1
                print("{a} of {b} video titles do not exist as Spotify playlists ({g}%)".format(a=d, b=c, g=round((d/c)*100, 2)))
            c += 1 

def main():
    results_dict = read_results()
    playlist_item_list = collect_data(results_dict)
    write_csv(playlist_item_list, "data/unreleased/potential_playlists.csv")
main()