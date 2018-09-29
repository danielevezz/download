from bs4 import BeautifulSoup as bs
import requests
import csv
import time
import re
import youtube_dl
import taglib
import os
import string

# Simple script to get youtube link from a csv file containing the
# titles and the artist

# URL to form. At the end is appended the query, which are words separated by "+"
yt = "https://www.youtube.com/results?search_query="

urls = []
names = []

# Read the CSV
with open('songs.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    print("Urls generation")
    for row in spamreader:
        # title
        row[0] = string.capwords(row[0].strip())
        # artist
        row[1] = string.capwords(row[1].strip())
        if len(row) == 3:
            # album
            row[2] = string.capwords(row[2].strip())
        else:
            row.append("")
        names.append((row[0], row[1], row[2]))
        row = "+".join(row)
        row = row.strip()
        row = row.replace(" ", "+")

        url1 = yt + row
        print(url1)
        urls.append(url1)

watch = []

# Using requests to send a get request to the urls
print("Start request")
for url in urls:
    page = requests.get(url, headers={"User-Agent": "Requests"}).content
    soup = bs(page, "html.parser")

    # Finding the first link that is a video and not an ad
    print(f"video: {url}")
    for link in soup.find_all("a"):
        href = link.get("href")
        if "/watch" in href:
            videoLink = "http://youtube.com" + href
            # if it is an ad,skip
            if "googleadservice" in videoLink:
                continue
            watch.append(videoLink)
            print(videoLink)
            break

    # sleeping 15 seconds to not send too many request to server
    # don't know if necessary
    if url != urls[-1]:
        time.sleep(15)

# ids = []
#
# getId = re.compile(r"youtu(?:.*\/v\/|.*v\=|\.be\/|.*?embed\/)([A-Za-z0-9_\-]{11})")
#
# for v in watch:
#     ids.append(getId.split(v)[1])
#
#
# videos_id = ','.join([str(x) for x in ids])

# generate playlist link to easier download
# i think max is 50 songs with this url
# playlist_link = "https://www.youtube.com/watch_videos?video_ids=" + videos_id

# append to file
print(watch)
with open("video_links.txt", "a+") as output:
    # output.write(playlist_link + "\n")
    for yt_link in watch:
        output.write(yt_link + "\n")


# Download songs with youtube-dl
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'nocheckcertificate': True,
    'outtmpl': ''
}

os.chdir("music")

for song in zip(watch, names):
    print(song)
    #(link, (title, artist))
    title = song[1][0]
    artist = song[1][1]
    album = song[1][2]

    ydl_opts['outtmpl'] = f'{title} - {artist}.mp3'

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([song[0]])

    file = taglib.File(f'{title} - {artist}.mp3')
    if file:
        file.tags["TITLE"] = [title]
        file.tags["ARTIST"] = [artist]
        file.tags["ALBUM"] = [album]
        file.save()
