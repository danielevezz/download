from bs4 import BeautifulSoup as bs
import requests
import csv
import time
import re
import youtube_dl

# Simple script to get youtube link from a csv file containing the 
# titles and the artist

# URL to form. At the end is appended the query, which are words separated by "+"
yt = "https://www.youtube.com/results?search_query="

urls = []

# Read the CSV
with open('songs.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    print("Urls generation")
    for row in spamreader:
        row [0] = row[0].strip()
        row [1] = row[1].strip()
        row = "+".join(row)
        row = row.strip()
        row = row.replace(" ", "+")

        url1 = yt + row
        print(url1)
        urls.append(url1)

watch  = []

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
#playlist_link = "https://www.youtube.com/watch_videos?video_ids=" + videos_id 

# append to file
print(watch)
with open("video_links.txt", "a+") as output:
    #output.write(playlist_link + "\n")
    for yt_link in watch:
        output.write(yt_link + "\n")
print("done")


# Download songs with youtube-dl
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'nocheckcertificate': True,
    'outtmpl' : 'music/%(title)s.%(ext)s'
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    for song in watch:
        ydl.download([song])
