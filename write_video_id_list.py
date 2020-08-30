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


def is_file_empty(filename):
    with open(filename) as empty_file:
        first_char = empty_file.read(1)
        if not first_char:
            print('file is empty')
            return True
        else:
            return False


def get_youtube_api(filename):
    api_key = ''
    with open(filename, 'r') as yt_file:
        api_key = yt_file.read().replace('\n', '')
    return api_key


def get_video_ids_from_api(current_ids):
    next_page = ''
    ids = youtube.get_videos_from_playlist_id(playlist_id, next_page)

    ret_ids = []
    for single_id in ids:
        if single_id not in current_ids:
            ret_ids.append(single_id)

    return ret_ids


def construct_video_id_array(video_data_file):
    with open(video_data_file, 'r') as file:
        data = json.load(file)

    video_ids_separate = []
    for video in data:
        video_ids_separate.append(video['video_id'])

    return video_ids_separate


def write_video_ids_to_file(video_ids, video_data_file):
    # clear file, maybe check if it's empty first before doing this
    file_is_empty = is_file_empty(video_data_file)
    if file_is_empty:
        open(video_data_file, 'w').close()

    with open(video_data_file, 'a') as file:
        json.dump(video_ids, file, indent=4, sort_keys=True, default=str)
        print('collecting video ids')


def get_video_snippet_data(video_data_file):
    with open(video_data_file, 'r') as data_file:
        video_ids_json = json.load(data_file)

    counter = 0
    video_snippets_data = []
    for video in video_ids_json:
        video_id = str(video['video_id'])
        # time.sleep(1)  # Sleep for 1 second so Google doesn't get mad and close the connection
        snippet = youtube.get_video_metadata(video_id, part=['snippet'])
        video_snippets_data.append(snippet)
        print('video #'+str(counter)+', processing snippet for: '+video_id)
        counter += 1

    return video_snippets_data


def write_video_snippets_to_file(video_snippets_data, snippets_file_name):
    # clear file
    open(snippets_file_name, 'w').close()

    with open(snippets_file_name, 'a') as file:
        print('dumping snippets to file')
        file.write('{')
        json.dump(video_snippets_data, file, indent=4, sort_keys=True, default=str)
        file.write('}')


if __name__ == "__main__":
    # replace with your api key in the youtube-api-key file
    # get youtube api key from file
    yt_api = get_youtube_api(yt_api_file)
    youtube = YouTubeDataAPI(yt_api)
    video_id_file = 'video_data.json'

    # read current files to populate ids and prevent duplicate downloads of data
    current_ids = construct_video_id_array(video_id_file)

    # get video ids from API
    get_video_ids = get_video_ids_from_api(current_ids)

    # write data to file
    write_video_ids_to_file(get_video_ids, video_id_file)

    ###TODO ok so the video ids are handling duplicates well now, just need to do that for snippets vs. the video_data file
    # get snippets for each video using ids
    # this contains meta data about each video useful for data labeling and organization later
    snippets = get_video_snippet_data(video_id_file)

    # write snippets to file
    snippets_file = 'video_snippets.json'
    write_video_snippets_to_file(snippets, snippets_file)

    ###TODO insert section in snippets data for storing the transcription data
    ###TODO iterate through the IDs and get a transcription for each, storing them in that slot



