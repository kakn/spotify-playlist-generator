import csv

def read_and_sort_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # skip the header row
        next(reader)
        # sort the data by the third index (converted to int) in descending order
        sorted_data = sorted(reader, key=lambda row: int(row[2]), reverse=True)
        return sorted_data

def check_video_title():
    """
    This function counts how many video titles contain the phrases listed in 'avoid'.
    """
    file_path = 'potential_playlists.csv'
    sorted_data = read_and_sort_csv(file_path)
    avoid = ['official', 'lyrics', 'video', 'audio', 'directed']
    counter = 0
    for item in sorted_data:
        c = 0
        for item2 in avoid:
            if item2 in item[0].lower():
                c += 1
        if c != 0:
            counter += 1
        print(item)
    print(counter)

import re 

from emoji import demojize

def remove_emojis(text):
    # The function demojize() replaces unicode emoji with the emoji name surrounded by ":".
    text = demojize(text)
    
    # Remove all emojis using a regular expression that matches the emoji names.
    return re.sub(r':[a-z_]+:', '', text)

def strip_leading_trailing_quotes(title):
    # Find all leading and trailing quotation marks
    leading_quotes = re.findall(r'^\"+', title)
    trailing_quotes = re.findall(r'\"+$', title)

    # If there are any leading or trailing quotes
    if leading_quotes and trailing_quotes:
        # Count the number of leading and trailing quotes
        leading_count = len(leading_quotes[0])
        trailing_count = len(trailing_quotes[0])

        # Determine the minimum number of quotes to remove
        min_quotes = min(leading_count, trailing_count)

        # Remove min_quotes from both the start and end of the string
        title = title[min_quotes:-min_quotes]

    return title

def simple_strip_quotations(title):
    num_quot = 0
    for character in title:
        if character == '\"':
            num_quot += 1
    if num_quot == 2:
        if title.startswith('\"') and title.endswith('\"'):
            title = title[1:-1]
    return title

def regex_methods(video_title):
    
    pattern = [
        [r'[\[\(][^()]*Music[^()]*[\]\)]', ''], # any string within [] or () that contains 'Music'.
        [r'[\[\(][^()]*Explicit[^()]*[\]\)]', ''], # any string within [] or () that contains 'Explicit'.
        [r'[\[\(][^()]*Lyrics[^()]*[\]\)]', ''], # any string within [] or () that contains 'Lyrics'.
        [r'[\[\(][^()]*Directed[^()]*[\]\)]', ''], # any string within [] or () that contains 'Directed'.
        [r'[\[\(][^()]*Video[^()]*[\]\)]', ''], # any string within [] or () that contains 'Video'.
        [r'[\[\(][^()]*Audio[^()]*[\]\)]', ''], # any string within [] or () that contains 'Audio'.
        [r'[\[\(][^()]*Visual[^()]*[\]\)]', ''], # any string within [] or () that contains 'Visual'.
        [r'[\[\(][^()]*Unreleased[^()]*[\]\)]', ''], # any string within [] or () that contains 'Unreleased'.
        [r' +', ' '] # one or more spaces
    ]

    stripped_title = video_title

    for p in pattern:
        stripped_title = re.sub(p[0], p[1], stripped_title).strip()
        stripped_title = re.sub(p[0].lower(), p[1], stripped_title).strip() # lowercase
        stripped_title = re.sub(p[0].upper(), p[1], stripped_title).strip() # uppercase
    return stripped_title

from sp_check_song_exists import find_track_on_spotify
from sp_check_playlist_exists import playlist_exists

def strip_video_title(sorted_file):
    """
    This file takes the sorted list of potential playlists and strips them of video title scrap.
    It then checks if the title exists as a song on Spotify.
    Finally, it writes to a list of our final candidates for playlists
    """
    file_path = "data/final_playlist_candidates.csv"
    counter = 0
    for title in sorted_file:
        counter += 1
        original_title = title[0]
        stripped_title = regex_methods(original_title)
        if playlist_exists(stripped_title):
            print("(ID {i}): Playlist '{a}' already exists!".format(i=counter, a=stripped_title))
            continue
        modified_title = [stripped_title] + title[1:]
        with open(file_path, "a", encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(modified_title)
        
from preprocess_yt_videos import rotate_openai_api
import csv 

def separate_artist_song(stripped_title: str):
    for i in range(len(stripped_title)):
        if stripped_title[i] == "-":
            artist_name = stripped_title[:i].strip()
            song_name = stripped_title[i+1:].strip()
            return artist_name, song_name
    return None, None

def separate_artist_song_ai(sorted_file):
    """
    This file should update/create a new 'potential_playlists.csv',
    removing entries that exist as songs. The output found in this function
    should be passed to "check_song_exists". Finally, I think the final files
    could be stripped of video title fluff.
    """
    song_artist_file_path = "data/song_artist.csv"
    song_data = []
    for line in sorted_file[1:]:
        video_title = line[0]
        artist, song, ignore = rotate_openai_api(video_title)
        song_data.append([artist, song])
    with open(song_artist_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Artist", "Song"])
        # Write the data
        for row in song_data:
            writer.writerow(row)

def strip_quotations_unicode(sorted_file):
    file_path = "data/new_final_playlist_candidates.csv"
    counter = 0
    for item in sorted_file:
        title = item[0]
        counter += 1
        title_stripped = title.replace("\"", "") # strips all quotation marks
        strip_unicode = title_stripped.replace('[U+200E]', '') # strips this unicode
        strip_unicode = strip_unicode.replace('\u200E', '')
        stripped_spaces = re.sub(r' +', ' ', strip_unicode).strip()
        if playlist_exists(stripped_spaces):
            print("(ID {i}): Playlist '{a}' already exists!".format(i=counter, a=stripped_spaces))
            continue
        modified_title = [stripped_spaces] + item[1:]
        with open(file_path, "a", encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(item)
        
def main():
    sorted_data = read_and_sort_csv('data/new_final_playlist_candidates.csv')
    # separate_artist_song(sorted_data)
    check_if_on_spotify(sorted_data)
main()