import json
import re
import csv
import openai
import time

outlook = "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"
kasperknudsen85 = "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"
rigbytf = "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"
rigbyroo = "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"
mia = "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"
API_KEYS = [outlook, kasperknudsen85, rigbytf, rigbyroo, mia]

def read_results():
    results = open('result4.json')
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

def openai_artist_and_song(videotitle, last_api_key_index):
    openai.api_key = API_KEYS[last_api_key_index]
    prompt = "Given the following YouTube video title, output the artist name (including features) and the song name: \n"
    final_prompt = prompt + videotitle
    model = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": final_prompt}], 
                                         max_tokens=1024, n=1, stop=None, temperature=0.5)
    response = model['choices'][0]['message']['content']
    pattern = r":\s*(.*)\n.*:\s*(.*)"
    matches = re.search(pattern, response)
    if matches:
        match1 = matches.group(1)
        match2 = matches.group(2)
        print("Artist:", match1, "Song:", match2)
        return match1, match2, last_api_key_index
    else:
        print("No match for {a}".format(a=videotitle))
        response = response.replace('\n', '')
        print("Received response: '{b}'...".format(b=response[:30]))
        return None, None, last_api_key_index

def rotate_openai_api(videotitle, last_api_key_index=0):
    try:
        return openai_artist_and_song(videotitle, last_api_key_index)
    except (openai.error.APIConnectionError, openai.error.APIError, TimeoutError) as e:
        # except bad gateway
        print("Caught {a}".format(a=e))
        time.sleep(5)
        return rotate_openai_api(videotitle, last_api_key_index)
    except openai.error.RateLimitError:
        print(f"Rate limit exceeded for API key {API_KEYS[last_api_key_index]}")
        next_index = (last_api_key_index + 1) % len(API_KEYS)
        time.sleep(5)
        return rotate_openai_api(videotitle, last_api_key_index=next_index)

def write_csv(items, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:
            writer.writerow(['Video Title', 'Video ID', 'View Count', 'Thumbnail URL'])
        last_key_index = 0
        so_far = 16912 # 22:52 pm
        c = so_far
        for item in items[so_far:]:
            print("Item {a} of {b}".format(a=c, b=len(items)-1)) # implement percentages
            artist, song, last_key_index = rotate_openai_api(item[0], last_key_index)
            if artist != None:
                item[0:1] = [artist, song]
                writer.writerow(item)
            c += 1

def main():
    results_dict = read_results()
    playlist_item_list = collect_data(results_dict)
    write_csv(playlist_item_list, 'songlist.csv')
# main()
