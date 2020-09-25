from datetime import timedelta
from bson import json_util
import json
import requests
import sys
import os
import pandas as pd
from youtube_api import YouTubeDataAPI
import time
from youtube_transcript_api import YouTubeTranscriptApi
import couchdb

# YouTube API wrapper used: https://youtube-data-api.readthedocs.io/en/latest/youtube_api.html

# replace with your playlist_id
playlist_id = 'UU9CuvdOVfMPvKCiwdGKL3cQ'

# this is the google API key
yt_api_file = 'youtube-api-key'

couch = {}
video_data_database = {}
snippets_database = {}


def is_file_empty(filename):
    with open(filename) as empty_file:
        first_char = empty_file.read(1)
        empty_file.close()
        if not first_char:
            print('file' + filename + ' is empty')
            return True
        else:
            print('file' + filename + ' is NOT empty')
            return False

#region YouTube Stuff
def get_youtube_api(filename):
    api_key = ''
    with open(filename, 'r') as yt_file:
        api_key = yt_file.read().replace('\n', '')
        yt_file.close()

    return api_key


def get_video_ids_from_api(current_video_ids):
    next_page = ''
    ids = youtube.get_videos_from_playlist_id(playlist_id, next_page)

    ret_ids = []
    for single_id in ids:
        if single_id not in current_video_ids:
            ret_ids.append(single_id)

    return ret_ids
#endregion YouTube Stuff

def construct_video_id_array(video_data_file):
    with open(video_data_file, 'r') as file:
        json_data = json.load(file, object_hook=json_util.object_hook)
        file.close()

    video_ids_separate = []
    for video in json_data['video_data']:
        insert_video_data_in_db(video)
        video_ids_separate.append(video['video_id'])

    return video_ids_separate


def create_valid_json_file(key_string, file_name):
    with open(file_name, 'r+') as file:
        first_line = file.readline()
        if key_string not in first_line:
            content = file.read()
            file.seek(0, 0)
            file.truncate(0)  # clear file
            file.write('{\"'+key_string+'\":[\n'+content)
            print('formatting file properly')
        file.close()

    with open(file_name, 'rb+') as file:
        file.seek(file.tell()-1, 2)
        last_line = file.read()
        if '}'.encode() not in last_line:
            file.write("}".encode())
        file.close()


def get_video_snippet_data(video_data_file, current_snippets_file):
    # video_ids = get_video_data_from_db()
    with open(video_data_file, 'r') as data_file:
        video_ids_json = json.load(data_file, object_hook=json_util.object_hook)
        data_file.close()

    counter = 0
    video_snippets_data = []
    current_snippet_video_ids = find_non_duplicate_snippets(current_snippets_file)

    for video in video_ids_json['video_data']:
        video_id = video['video_id']

        if video_id not in current_snippet_video_ids:
            # time.sleep(1)  # Sleep for 1 second so Google doesn't get mad and close the connection
            snippet = youtube.get_video_metadata(video_id, part=['snippet'])
            snippet_json_string = json.dumps(snippet, indent=4, sort_keys=True, default=str)
            # json.loads(snippet_json_string, object_hook=json_util.object_hook)
            snippet = json.loads(snippet_json_string, object_hook=json_util.object_hook)
            insert_video_snippet_in_db(snippet)
            video_snippets_data.append(snippet)
            print('video #'+str(counter)+', processing snippet for: '+video_id)
            counter += 1
        # else:
        #     print('video '+video_id+' is already in snippets file')

    return video_snippets_data


def find_non_duplicate_snippets(current_snippets_file):
    with open(current_snippets_file, 'r') as file:
        current_snippets = json.load(file, object_hook=json_util.object_hook)
        # write_video_snippets_to_db(current_snippets, current_snippets_file)
        file.close()

    # Insert snippet into db
    snippet_video_ids = []
    for snippet in current_snippets['video_snippets']:
        insert_video_snippet_in_db(snippet)
        snippet_video_ids.append(snippet['video_id'])

    return snippet_video_ids


# def write_video_snippets_to_file(video_snippets_data, snippets_file_name):
#     # create and clear file if it's empty
#     file_is_empty = is_file_empty(snippets_file_name)
#     if file_is_empty:
#         open(snippets_file_name, 'w').close()
#
#     with open(snippets_file_name, 'r+') as file:
#         json.dump(video_snippets_data, file, indent=4, sort_keys=True, default=json_util.object_hook)
#         print('dumping snippets to file')
#         file.close()
#
#     create_valid_json_file('video_snippets', snippets_file_name)


#region DB Stuff
def init_couch_db():
    # Link to couchdb: http://localhost:5984/_utils/#/_all_dbs
    global couch
    couch = couchdb.Server("http://admin:1223@localhost:5984")
    global video_data_database
    if 'video_ids_database' not in couch:
        video_data_database = couch.create('video_ids_database')
    else:
        video_data_database = couch['video_ids_database']

    global snippets_database
    if 'video_snippets_database' not in couch:
        snippets_database = couch.create('video_snippets_database')
    else:
        snippets_database = couch['video_snippets_database']


def update_video_snippet(video_snippet):
    video_id = video_snippet['video_id']
    channel_id = video_snippet['channel_id']
    key = channel_id+video_id
    # video_snippet_string = json.dumps(video_snippet, indent=4, sort_keys=True, default=str)
    # video_snippet_dict = json.loads(video_snippet_string, object_hook=json_util.object_hook)
    if snippets_database is not None:
        snippets_database[key]['subtitles'] = video_snippet['subtitles']
        # snippets_database[key] = video_snippet_dict


def is_key_in_db(key, database):
    if database[key] is None:
        return False
    else:
        return True
def write_video_ids_to_db(video_ids, video_data_file):
    for video in video_ids:
        insert_video_data_in_db(video)

    create_valid_json_file('video_data', video_data_file)


def write_video_snippets_to_db(video_snippets, video_snippets_file):
    for snippet in video_snippets:
        insert_video_snippet_in_db(snippet)

    create_valid_json_file('video_snippets', video_snippets_file)


def get_video_data_from_db():
    video_ids = []
    for document in video_data_database:
        print("retrieving document: "+document)
        video_data = video_data_database[document]
        video_ids.append(video_data)

    return video_ids


def insert_video_data_in_db(video_data):
    # print('inserting '+video_data['video_id']+' into table '+str(table))
    video_id = video_data['video_id']
    channel_id = video_data['channel_id']
    key = channel_id+video_id
    if video_data_database is not None and key not in video_data_database:
        video_data_database[key] = video_data
    else:
        if video_data_database.get(key) is None:
            print('missed key, inserting '+key)
            video_data_database[key] = video_data
        # else:
        #     # print(key+' already in database')


def insert_video_snippet_in_db(video_snippet):
    video_id = video_snippet['video_id']
    channel_id = video_snippet['channel_id']
    key = channel_id+video_id
    # video_snippet_string = json.dumps(video_snippet, indent=4, sort_keys=True, default=str)
    # video_snippet_dict = json.loads(video_snippet_string, object_hook=json_util.object_hook)
    if snippets_database is not None and key not in snippets_database:
        # snippets_database[key] = video_snippet_dict
        snippets_database[key] = video_snippet
    else:
        if snippets_database.get(key) is None:
            print('missed key, inserting '+key)
            snippets_database[key] = video_snippet
            # snippets_database[key] = video_snippet_dict
        # else:
        #     # print(key+' already in database')
#endregion DB Stuff

def get_video_transcriptions():
    for snippet in video_snippets:
        try:
            print('getting transcript from '+snippet['video+id'])
            snippet['subtitles'] = YouTubeTranscriptApi.get_transcript(snippet['video_id'])
            update_video_snippet(snippet)
        except Exception as exception:
            print("no transcriptions for video: https://www.youtube.com/watch?v="+snippet['video_id'])


if __name__ == "__main__":
    # initialize db
    init_couch_db()

    # replace with your api key in the youtube-api-key file
    # get youtube api key from file
    yt_api = get_youtube_api(yt_api_file)
    youtube = YouTubeDataAPI(yt_api)
    video_id_file = 'video_data.json'
    snippets_file = 'video_snippets.json'

    # ensure files have a valid key at the beginning
    print('creating valid json files')
    create_valid_json_file('video_data', video_id_file)
    create_valid_json_file('video_snippets', snippets_file)

    # read current files to populate ids and prevent duplicate downloads of data
    print('getting current video ids')
    current_ids = construct_video_id_array(video_id_file)

    # get video ids from API
    print('getting video ids from api')
    get_video_ids = get_video_ids_from_api(current_ids)

    # # write data to file
    # print('writing new ids to file')
    # write_video_ids_to_db(get_video_ids, video_id_file)

    # Fixed this by using database instead:
    # alright so we have a different issue now: this very large JSON is not being handled well by Python
    # we need to get a library that acts upon it as a stream instead, as there are some corruptions about halfway
    # through writing the file

    # get snippets for each video using ids
    # this contains meta data about each video useful for data labeling and organization later
    print('getting video snippets data')
    snippets = get_video_snippet_data(video_id_file, snippets_file)

    # write snippets to file
    print('writing snippets to file')
    write_video_snippets_to_db(snippets, snippets_file)

    # get transcriptions and save to db
    get_video_transcriptions(snippets)

    ###TODO replace all the files with the database since it's populated now (except for transcriptions)
        # This will fix the file corruption issues when reading/writing the json
    ###TODO insert section in snippets data for storing the transcription data
    ###TODO iterate through the IDs and get a transcription for each, storing them in that slot



