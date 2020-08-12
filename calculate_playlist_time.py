from datetime import timedelta
import isodate
import json
import requests

# replace with your api
yt_api = ''
# replace with your playlist_id
playlist_id = 'UU9CuvdOVfMPvKCiwdGKL3cQ'

URL1 = 'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId,nextPageToken&key={}&playlistId={}&pageToken='.format(
    yt_api, playlist_id)
URL2 = 'https://www.googleapis.com/youtube/v3/videos?&part=contentDetails&key={}&id={}&fields=items/contentDetails/duration'.format(
    yt_api, '{}')

next_page = ''
cnt = 0
a = timedelta(0)

while True:
    vid_list = []

    results = json.loads(requests.get(URL1 + next_page).text)

    for x in results['items']:
        vid_list.append(x['contentDetails']['videoId'])

    url_list = ','.join(vid_list)
    cnt += len(vid_list)

    op = json.loads(requests.get(URL2.format(url_list)).text)
    for x in op['items']:
        a += isodate.parse_duration(x['contentDetails']['duration'])
        print('found: '+str(a.total_seconds())+' in video time so far')

    if 'nextPageToken' in results:
        next_page = results['nextPageToken']
    else:
        original_stdout = sys.stdout
        with open('Game Grumps Video Stats - '+playlist_id+'.txt', 'w') as f:
            sys.stdout = f
            print('Here are some stats on the Game Grumps playlist: ')
            print('No of videos :' + str(cnt),
                  '\nAverage length of video :' + str(a / cnt),
                  '\nTotal length of playlist :' + str(a),
                  '\nAt 1.25x :', str(a / 1.25),
                  '\nAt 1.50x :', str(a / 1.5),
                  '\nAt 1.75x :', str(a / 1.75),
                  '\nAt 2.00x :', str(a / 2))

        sys.stdout = original_stdout
        break

