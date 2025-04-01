from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import sys

# Figure out if im using result2 or result3 --> len(p)
# Figure out playlist HttpError
# Figure out 2723 or 2725

# Except 403 error (quota) and 404 (no playlist) and others (idk)
# Have fuck tons of backups on errors

kasperknudsen = "===REDACTED==="
kasperknudsen85 = "===REDACTED===-NwhQ"
thomasgartside = "===REDACTED==="
rigbyroo = "===REDACTED==="
rigbytf = "===REDACTED==="
devs = [kasperknudsen, kasperknudsen85, thomasgartside, rigbyroo, rigbytf]

# DEVELOPER_KEY = kasperknudsen
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

max_results = 50
# with open('result3.json') as json_file:
#     videos = json.load(json_file)
videos = {}
#print(videos)
# print(len(videos))
# print(type(videos))
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
        # vidz = vidz['items'][0]['statistics']
        # print(type(vidz))
        search_result = {**search_result, **vidz}
        if owner not in videos:
            videos[owner] = [search_result]
        
    try:
        nextPageToken = search_response['nextPageToken']
        playlist_parser(playlistId, nextPageToken, dkey)
        #print("recursion!")
    except KeyError:
        nextPageToken = None
    except TypeError:
        nextPageToken = None
    #print(videos)
    print(len(videos))

def tryTryAgain(line, i, c, f):
    # function that rotates developer keys to bypass google api quotas
    if i == 5:
         with open('result4.json', 'w') as fp:
                print("Final number of songs: {a}".format(a=len(videos)))
                json.dump(videos, fp)
    try:
        playlist_parser(line, None, devs[i])
        print("dev [{k}]: Loop {a} of {b} complete ({c}%)".format(k=devs[i], a=c+2723, b=len(f), c=((c+2723)/len(f))*100))
        # REMEMBER: Loop a is not the a_th index in pls.txt, but the a-1_th 
        # Broke at completed loop 1039
        # Second time broke at 2300
        # Third at 2724
    except HttpError as h:
        # print(h)
        #e = sys.exc_info()[0]
        if h.resp.status == 403:
            i += 1
            tryTryAgain(line, i, c, f)
        elif h.resp.status == 404:
            print("Skipped")
        else:
            print("wat!!!")
    except TimeoutError:
        with open('result4.json', 'w') as fp:
                print("Final number of songs: {a}".format(a=len(videos)))
                json.dump(videos, fp)
    
def main():
    f = open('pls.txt').readlines()
    c = 1
    for line in f[2723:]:
        line = line.strip() 
        #print(line)
        tryTryAgain(line, 0, c, f)
        c += 1
    with open('result4.json', 'w') as fp:
        json.dump(videos, fp)
    f.close()
main()