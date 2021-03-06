import sys
import youtube_dl
import time

# setting the user agent so that youtube can't stop be from downloading a massive amount of videos
#youtube_dl.utils.std_headers['User-Agent'] = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

# OK Time to download the youtube videos
# Helper functions
def format_bytes(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return '{:.1f}'.format(size), power_labels[n] + 'bytes'


ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

with ydl:
    result = ydl.extract_info(
        'https://www.youtube.com/watch?v=RBQYs4S_5m0',
        download=False  # just want to extract the info
    )

if 'entries' in result:
    # Can be a playlist of a list of videos
    video = result['entries'][0]
else:
    # Just a video
    video = result

print(video)
video_url = video['webpage_url']
print(video_url)

# get all format types from the video
formats = video['formats']
smallestFileSize = sys.maxsize

# print all formats
for f in formats:
    fileSize = f['filesize']
    formattedFileSize = ''
    if fileSize is not None:
        smallestFileSize = fileSize if fileSize < smallestFileSize else smallestFileSize
        formattedFileSize = format_bytes(fileSize)
    fileSizeString = str(formattedFileSize)
    print(f['format'] + ' - fileSize: ' + fileSizeString)

duration = video['duration']
bytesPerSecond = smallestFileSize / duration
print(
    'smallest file size is: '+str(format_bytes(smallestFileSize))+', video - bytes per second: ' + str(bytesPerSecond)
)


# ok now actually download the videos
# SAVE_PATH = 'E:\\Game Grumps Audio Files\\'
SAVE_PATH = '%UserProfile%\\Music\\Game Grumps Audio'


ydl_opts = {
    'format': 'worstaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '249',
    }],
    'verbose': 'true',
    'outtmpl': SAVE_PATH + '/%(title)s.%(ext)s',
    'cookiefile': '%UserProfile%\\Documents\\Google\\cookies.txt',
    # 'playliststart': 0,
    'prefer_free_formats': 'true',
    'download_archive': 'gamegrumpsarchive.txt'
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # ydl.download(['https://www.youtube.com/watch?v=Ff291Mq2nJ0'])
    # commenting out the playlist right now as it wasn't working :(
    start = time.time()
    ydl.download(['https://www.youtube.com/playlist?list=UU9CuvdOVfMPvKCiwdGKL3cQ'])
    end = time.time()

print('total time elapsed for this playlist download: '+str(end - start))


# These comments below are no longer valid but leaving them in for learning purposes

# Looks like there is some kind of 'age gating' issue with some of the videos. Need to install and run googlebot
# remove cookies: https://www.reddit.com/r/youtubedl/comments/hrieui/getting_error_youtube_said_unable_to_extract/

# Ok tried user agent, still not working. Keep an eye on the reddit thread asking for help:
# https://www.reddit.com/r/youtubedl/comments/i86qsl/trying_to_download_the_audio_from_an_entire/

# READ THIS GUIDE, might help with the issues:
# https://letswp.io/download-entire-youtube-channel/
# ok it doesn't but it'll help when I need to automate the downloads in the future to update the site
