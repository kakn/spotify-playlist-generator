import json
import re

def read_results():
    results = open('result4.json')
    results_dict = json.load(results)
    results.close()
    return results_dict

def clean_title(title):
    regex = r"\(\s*(Official\s+)?(Music\s+)?(Video|Lyric(s)?)\s*\)|\s*\[(HD|Official\s+Video)\]\s*|\s*(Lyric(s)?\s+)?-?\s*(Official\s+)?(Music\s+)?(Video|Audio)\s*"
    match = re.sub(regex, "", title)
    return match

def collect_data(results_dict):
    playlist_item_list = []
    for result in results_dict.items():
        dict_key = result[0]
        dict_items = results_dict[dict_key]
        data = dict_items[0]
        try:
            title = str(data['snippet']['title'])
            description = str(data['snippet']['description'])
            description = re.sub('\n', ' ', description)
            video_id = str(data['contentDetails']['videoId'])
            thumbnail_url = str(data['snippet']['thumbnails']['default']['url'])
            view_count = int(data['items'][0]['statistics']['viewCount'])
            playlist_item_list.append([title, description, video_id, view_count, thumbnail_url])
        except (KeyError, IndexError, UnicodeEncodeError):
            continue
    return playlist_item_list

def main():
    results_dict = read_results()
    playlist_item_list = collect_data(results_dict)
    # final_list = create_final_list(playlist_item_list)
    print(len(playlist_item_list))
main()
