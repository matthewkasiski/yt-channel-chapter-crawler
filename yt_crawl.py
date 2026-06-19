#!/usr/bin/env python3

import os
import requests
import re
import json
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,  # or INFO, WARNING, ERROR
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


TIMESTAMP_RE = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{2}):(\d{2})")
API_URL = "https://www.googleapis.com/youtube/v3"


class SearchEntry:
    # JSON serializey stuff
    class Timestamp:
        hours = 0
        minutes = 0
        seconds = 1

    videoTitle = ""
    videoId = ""
    timestamp = Timestamp()
    tag = ""
    line = ""

    def __init__(self, videoTitle, video, hours, minutes, seconds, tag, line):
        (
            self.videoTitle,
            self.videoId,
            self.timestamp.hours,
            self.timestamp.minutes,
            self.timestamp.seconds,
            self.tag,
            self.line,
        ) = (videoTitle, video, hours, minutes, seconds, tag, line)

    def AsJsonSerializable(self):
        return {
            "videoTitle": self.videoTitle,
            "videoId": self.videoId,
            "timestamp": {
                "hours": int(self.timestamp.hours),
                "minutes": int(self.timestamp.minutes),
                "seconds": int(self.timestamp.seconds),
            },
            "tag": self.tag,
            "line": self.line,
        }


def GetUploadChannel(api_key, channel_id):
    # YouTube API will only return a list of videos in a playlist, not channel.
    # This will get the playlist that contains all videos.
    data = {"id": channel_id, "key": api_key, "part": "contentDetails"}
    r = requests.get(f"{API_URL}/channels", params=data)
    response = json.loads(r.text)
    # ToDo: There's gotta be a better way to do this...
    upload_id = (
        response.get("items")[0]
        .get("contentDetails")
        .get("relatedPlaylists")
        .get("uploads")
    )
    return upload_id


def GetTotalVideosInChannel(api_key, channel_id):
    # Get the total number of videos, so our playlist crawler knows how many videos to grab.
    # Probably is not needed, had created this before investigating how YouTube returns pages
    # in a query.
    data = {
        "key": api_key,
        "playlistId": GetUploadChannel(api_key=api_key, channel_id=channel_id),
        "part": "snippet",
        "maxResults": "2",
    }
    r = requests.get(f"{API_URL}/playlistItems", params=data)
    response = json.loads(r.text)
    total_videos = response.get("pageInfo").get("totalResults")
    return total_videos


def GetVideosInChannel(api_key, channel_id):
    # Gets all the videos in a playlist, hardcoded to the Uploaded Playlist
    # https://www.googleapis.com/youtube/v3/playlistItems?playlistId={"uploads" Id}&key={API key}&part=snippet&maxResults=50
    output = []
    next_page_token = ""
    page = 1
    total_videos = GetTotalVideosInChannel(api_key=api_key, channel_id=channel_id)
    # This logic probably can be replaced by doing checks against the nextPageToken.
    while total_videos > 0:
        page += 1
        total_videos = total_videos - 50
        data = {
            "key": api_key,
            "playlistId": GetUploadChannel(api_key=api_key, channel_id=channel_id),
            "part": "snippet",
            "maxResults": "50",
        }
        if next_page_token:
            data.update({"pageToken": next_page_token})
        r = requests.get(f"{API_URL}/playlistItems", params=data)
        videos = json.loads(r.text)
        next_page_token = videos.get("nextPageToken")
        for video in videos.get("items"):
            vId = video.get("snippet").get("resourceId").get("videoId")
            date = video.get("snippet").get("publishedAt")
            title = video.get("snippet").get("title")
            description = video.get("snippet").get("description")
            output.append([date, vId, title, description])
    return output


def run(channel_id, api_key, datasetOutputLocation):
    videos = []
    tags = {}

    print("Grabbing video list")
    output = GetVideosInChannel(api_key=api_key, channel_id=channel_id)
    print("Sorting data")
    for video in output:
        tag = ""
        description = video[3].split("\n")
        title = video[2]
        print(title)
        if title in tags.keys():
            tag = tags[title]
        for line in description:
            m = TIMESTAMP_RE.match(line)
            if not m:
                logger.debug("Skipped line (no time prefix): %r", line)
                continue

            h, mnt, sec = m.groups()
            hours = int(h) if h else 0
            minutes = int(mnt)
            seconds = int(sec)
            newline = line[m.end() :].strip()

            logger.debug(
                "Parsed time %02d:%02d:%02d from line: %r",
                hours,
                minutes,
                seconds,
                line,
            )

            entry = SearchEntry(
                title, video[1], hours, minutes, seconds, tag, newline
            ).AsJsonSerializable()

            videos.append(entry)

    print("Serializing dataset")
    dataset = json.dumps(videos)
    print("Writing Dataset dataset...")
    with open(datasetOutputLocation, "w") as ds:
        ds.write(dataset)


def cli():
    parser = argparse.ArgumentParser(description="Generate the dataset for the web app")
    parser.add_argument(
        "-c",
        "--yt_channel_id",
        help="Youtube Channel ID to parse (e.g. https://www.ytmaxer.com/tools/channel-id )",
        default=False,
        required=True,
    )
    parser.add_argument(
        "-a",
        "--yt_api_key",
        help="Your API key from the Youtube API. Optional set environment variable YT_CRAWL_YT_API_KEY",
        default=os.getenv("YT_CRAWL_YT_API_KEY"),
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="The output path of JSON file (e.g.dataset.json)",
        default="dataset.json",
    )
    args = parser.parse_args()

    if not args.yt_api_key:
        logger.error("No API key (-a) provided")

    run(args.yt_channel_id, args.yt_api_key, args.output_file)


if __name__ == "__main__":
    cli()
