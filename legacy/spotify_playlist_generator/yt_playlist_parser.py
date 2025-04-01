from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import sys

kasperknudsen = "===REDACTED==="
kasperknudsen85 = "===REDACTED==="
thomasgartside = "===REDACTED==="
rigbyroo = "===REDACTED==="
rigbytf = "===REDACTED==="
devs = [kasperknudsen, kasperknudsen85, thomasgartside, rigbyroo, rigbytf]

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

max_results = 50
# videos = {}
PROGRESS = 2726

# Uncomment this if I need to continue where I left off
with open('data/unreleased/youtube_videos_3.json') as json_file:
    videos = json.load(json_file)

def playlist_parser(playlistId, token, dkey):
    
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=dkey)

    if token is None:
        search_response = youtube.playlistItems().list(part='id,snippet,contentDetails', 
            playlistId=playlistId, maxResults=max_results).execute()
    else:
        search_response = youtube.playlistItems().list(part='id,snippet', 
            playlistId=playlistId, maxResults=max_results, pageToken=token).execute()

    for search_result in search_response.get('items', []):
        owner = search_result['snippet']['title']
        mitid = search_result['contentDetails']['videoId']
        vidz = youtube.videos().list(part='statistics',
        id=mitid).execute()
        search_result = {**search_result, **vidz}
        if owner not in videos:
            videos[owner] = [search_result]
        
    try:
        nextPageToken = search_response['nextPageToken']
        playlist_parser(playlistId, nextPageToken, dkey)
    except KeyError:
        nextPageToken = None
    except TypeError:
        nextPageToken = None

def tryTryAgain(line, i, c, f):
    # function that rotates developer keys to bypass google api quotas
    if i == 5:
         with open('data/unreleased/youtube_videos_4.json', 'w') as fp:
                print("Final number of songs: {a}".format(a=len(videos)))
                json.dump(videos, fp)
                quit()
    try:
        playlist_parser(line, None, devs[i])
        print("dev [{k}]: Loop {a} of {b} complete ({c}%)".format(k=devs[i], a=c+PROGRESS, b=len(f), c=((c+PROGRESS)/len(f))*100))
    except HttpError as h:
        if h.resp.status == 403:
            i += 1
            tryTryAgain(line, i, c, f)
        elif h.resp.status == 404:
            print("Skipped")
        else:
            print(f"Unknown error: {h}")
    except Exception as e:
        with open('data/unreleased/youtube_videos_4.json', 'w') as fp:
            print(f"Raised error: {e}")
            print("Final number of songs: {a}".format(a=len(videos)))
            json.dump(videos, fp)
            quit()
    
def main():
    f = open('data/unreleased/new_playlist_ids.txt').readlines()
    c = 1
    for line in f[PROGRESS:]:
        line = line.strip() 
        tryTryAgain(line, 0, c, f)
        c += 1
    with open('data/unreleased/youtube_videos_4.json', 'w') as fp:
        json.dump(videos, fp)
    f.close()

try:
    main()
except Exception as e:
    with open('data/unreleased/youtube_videos_4.json', 'w') as fp:
        print(f"Raised error: {e}")
        print("Final number of songs: {a}".format(a=len(videos)))
        json.dump(videos, fp)
        quit()