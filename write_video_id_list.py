from datetime import timedelta
import json
import requests
import sys
import os
import pandas as pd
from youtube_api import YouTubeDataAPI
import time
from youtube_transcript_api import YouTubeTranscriptApi

# YouTube API wrapper used: https://youtube-data-api.readthedocs.io/en/latest/youtube_api.html

# replace with your playlist_id
playlist_id = 'UU9CuvdOVfMPvKCiwdGKL3cQ'

# this is the google API key
yt_api_file = 'youtube-api-key'

def get_youtube_api(filename):
    api_key = ''
    with open(filename, 'r') as yt_file:
        api_key = yt_file.read().replace('\n', '')
    return api_key


# replace with your api key in the youtube-api-key file
yt_api = get_youtube_api(yt_api_file)
youtube = YouTubeDataAPI(yt_api)

next_page_token = ''
# video_ids = youtube.get_videos_from_playlist_id(playlist_id, next_page_token)
#
# # clear file
# open('video_data.json', 'w').close()
#
# with open('video_data.json', 'a') as file:
#     json.dump(video_ids, file, indent=4, sort_keys=True, default=str)
#     print('collecting video ids')

with open('video_data.json', 'r') as file:
    video_ids_json = json.load(file)


video_snippets_data = []
counter = 0
for video in video_ids_json:
    video_id = str(video['video_id'])
    time.sleep(1)  # Sleep for 1 second so Google doesn't get mad and close the connection
    snippet = youtube.get_video_metadata(video_id, part=['snippet'])
    video_snippets_data.append(snippet)
    print('video #'+str(counter)+', processing snippet for: '+video_id)
    counter += 1

# clear file
# open('video_snippets.json', 'w').close()

with open('video_snippets.json', 'a') as file:
    print('dumping snippets to file')
    json.dump(video_snippets_data, file, indent=4, sort_keys=True, default=str)


# text = YouTubeTranscriptApi.get_transcript("nUJussYbQDE")
# with open("BloodborneSampleTranscription", "w") as file:
#     file.write(str(text))

# URL1 = 'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId/title,nextPageToken&key={}&playlistId={}&pageToken='.format(
#     yt_api, playlist_id)
# URL2 = 'https://www.googleapis.com/youtube/v3/videos?&part=contentDetails&key={}&id={}&fields=items/contentDetails/duration'.format(
#     yt_api, '{}')
#
# next_page = ''
# cnt = 0
# a = timedelta(0)
# video_id_list = []
#
# while True:
#     vid_list = []
#
#     results = json.loads(requests.get(URL1 + next_page).text)
#
#     for x in results['items']:
#         vid_list.append(x['contentDetails']['videoId'])
#
#     url_list = ','.join(vid_list)
#     cnt += len(vid_list)
#
#     op = json.loads(requests.get(URL2.format(url_list)).text)
#     for x in op['items']:
#         vid_list.append(x['id'], x['title'])
#         # print('found: '+str(a.total_seconds())+' in video time so far')
#
#     if 'nextPageToken' in results:
#         next_page = results['nextPageToken']
#     else:
#         original_stdout = sys.stdout
#         with open('PlaylistIDs' + '.txt', 'w') as f:
#             sys.stdout = f
#             json.dumps(vid_list)
#
#         sys.stdout = original_stdout
#         break

# print('Filesize of all Game Grumps videos based on this file: '+str(bytesPerSecond*a.total_seconds()))
