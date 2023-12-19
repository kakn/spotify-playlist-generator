import os
import json

def create_music_json(directory):
    """
    Iterates through the given directory, creating a dictionary with folder and song names as keys,
    appending the artist's name, and paths to the corresponding .png file as values. 
    The dictionary is then saved as a JSON file.

    :param directory: Path to the directory containing music folders
    """
    music_dict = {}
    # Extract the artist's name from the directory path and format it
    artist_name = directory.split('/')[-1].replace('_', ' ')

    # Iterate through each folder in the directory
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)

        # Skip if not a directory
        if not os.path.isdir(folder_path):
            continue

        # Find the .png or .jpg file in the folder
        png_file = None
        for file in os.listdir(folder_path):
            if file.endswith('.png') or file.endswith('.jpg'):
                png_file = os.path.join(folder, file)
                break

        # If a .png or .jpg file is found, add the folder and its contents to the dictionary
        if png_file:
            key = f"{artist_name} - {folder}"
            music_dict[key] = os.path.join(directory, png_file)
            for file in os.listdir(folder_path):
                if file.endswith('.mp3') or file.endswith('.m4a'):
                    # Remove the numbering and file extension
                    song_name = ' '.join(file.split()[1:]).rsplit('.', 1)[0]
                    key = f"{artist_name} - {song_name}"
                    music_dict[key] = os.path.join(directory, png_file)

    # Save the dictionary as a JSON file
    with open('artist_playlists/music_data.json', 'w') as json_file:
        json.dump(music_dict, json_file, indent=4)

    return 'artist_playlists/music_data.json'

# Example usage
directory_path = 'data/artists/Alex_G'
create_music_json(directory_path)
