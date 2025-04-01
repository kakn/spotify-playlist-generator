import csv
import base64
import requests
from PIL import Image
from io import BytesIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import openai
import logging
from PIL import ImageEnhance

# Set up logging
logging.basicConfig(filename='playlist_generation.log', level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_related_tracks(sp, seed_tracks, total_tracks=50):
    try:
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=total_tracks)
        return [track['id'] for track in recommendations['tracks']]
    except Exception as e:
        logging.error(f"Error occurred while fetching related tracks: {str(e)}")
        return []

def generate_description(openai_api_key, title):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a 5 to 10 word description for a playlist with the title: {title}"}
            ]
        )
        description = response['choices'][0]['message']['content'].strip()
        description = description.strip('\"')
        if not description:
            logging.warning(f"Could not generate description for the title: {title}")
        return description
    except Exception as e:
        logging.error(f"Error occurred while generating description for the video title '{title}': {str(e)}")
        return ""

def generate_recommendation_tags(openai_api_key, title):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate recommendation tags for a playlist with the title: {title}"}
            ]
        )
        return response['choices'][0]['message']['content'].strip().split(", ")
    except Exception as e:
        logging.error(f"Error occurred while generating recommendation tags for the video title '{title}': {str(e)}")
        return []

def get_seed_tracks(sp, video_title):
    search_results = sp.search(q=video_title, limit=5, type='track')['tracks']['items']
    if search_results:
        return [track['id'] for track in search_results]

    extracted_info = generate_artist_or_genre(openai_api_key, video_title)
    if extracted_info:
        search_results = sp.search(q=extracted_info, limit=5, type='track')['tracks']['items']
        if search_results:
            return [track['id'] for track in search_results]

    return []

def generate_artist_or_genre(openai_api_key, title):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What artist or genre is mentioned in the title: {title}?"}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error occurred while generating artist or genre for the video title '{title}': {str(e)}")
        return ""

def enhance_image(image):
    try:
        enhancer = ImageEnhance.Sharpness(image)
        image_enhanced = enhancer.enhance(2.0)  # Adjust the enhancement factor as needed
        return image_enhanced
    except Exception as e:
        logging.error(f"Error occurred while enhancing image: {str(e)}")
        return None

def get_base64_image(url, video_title):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))

        # Enhance image only if it is of low resolution
        image = enhance_image(image)

        # Resize the image to a maximum of 640x640 pixels
        resized_image = image.resize((640, 640), Image.LANCZOS)

        output_buffer = BytesIO()
        resized_image.save(output_buffer, format='JPEG', quality=95)  # Saving image with high quality
        byte_data = output_buffer.getvalue()
        return base64.b64encode(byte_data).decode()
    except Exception as e:
        logging.error(f"Error occurred while getting base64 image for the video title '{video_title}': {str(e)}")
        return None

def create_playlist_from_csv(file_path, spotify_api_details, openai_api_key):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_api_details['client_id'],
                                                   client_secret=spotify_api_details['client_secret'],
                                                   redirect_uri="http://localhost:8000",
                                                   scope='playlist-modify-public ugc-image-upload',
                                                   open_browser=False))

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        total_rows = sum(1 for row in csv_file)
        csv_file.seek(0)

        for index, row in enumerate(csv_reader):
            video_title, _, _, thumbnail_link = row

            description_tags = generate_description(openai_api_key, video_title)

            try:
                print(f"\n({index + 1}/{total_rows}) Creating playlist: {video_title}")
                playlist = sp.user_playlist_create(user="31ecqbn3cnpznklsi6k5htlvhc5q", 
                                                   name=video_title, 
                                                   public=True, 
                                                   description=description_tags)

                base64_image = get_base64_image(thumbnail_link, video_title)
                if base64_image:
                    try:
                        sp.playlist_upload_cover_image(playlist['id'], base64_image)
                    except spotipy.exceptions.SpotifyException as e:
                        logging.error(f"Error occurred while uploading playlist image for the video title '{video_title}': {str(e)}")

                seed_tracks = get_seed_tracks(sp, video_title)
                if seed_tracks:
                    track_ids = get_related_tracks(sp, seed_tracks)
                    if track_ids:
                        sp.playlist_add_items(playlist['id'], items=track_ids)
                        print(f"Added {len(track_ids)} related tracks to playlist: {video_title}")
            except Exception as e:
                logging.error(f"Error occurred while creating playlist for the video title '{video_title}': {str(e)}")

spotify_api_details = {
    'client_id': '===REDACTED===',
    'client_secret': '===REDACTED==='
}

openai_api_key = "===REDACTED==="

create_playlist_from_csv('data/updated_candidates.csv', spotify_api_details, openai_api_key)