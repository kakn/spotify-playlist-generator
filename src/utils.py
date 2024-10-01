# utils.py

import re

def normalize_genre_name(genre):
    genre = genre.lower()
    genre = genre.replace(' ', '_')
    genre = re.sub(r'[^\w\-]', '', genre)
    return genre