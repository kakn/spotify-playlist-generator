from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEVELOPER_KEY = 'AIzaSyDsBUi46WUCuKXUK2H2o7Tq46w7fzourWY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

query = "not on spotify"
max_results = 50
initial = True
playlists = []

f = open('pls.txt', 'w')

def youtube_search(token):

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

    if token == 0:
        search_response = youtube.search().list(q=query, part='id,snippet',
            maxResults=max_results, type='playlist').execute()
    else:
        search_response = youtube.search().list(q=query, part='id,snippet',
            maxResults=max_results, type='playlist', pageToken=token).execute()

    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#playlist':
            playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                          search_result['id']['playlistId']))

    pwriter()
    token = search_response['nextPageToken']
    youtube_search(token)
    
def pwriter():
    print('Playlists:\n', '\n'.join(playlists), '\n')
    for p in playlists:
        k = p.split('(')[-1][:-1]
        f.write(k)
        f.write('\n')

def main():
    youtube_search(0)
main()