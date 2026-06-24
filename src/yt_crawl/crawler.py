import json
import logging
import re

from .models import SearchEntry, Timestamp
from .youtube_api import get_videos_in_channel

logger = logging.getLogger(__name__)

TIMESTAMP_RE = re.compile(r"^\s*(\d{1,2}:(?:\d{1,2}:)?\d{2})\b")


def parse_timestamp(line: str):
    m = TIMESTAMP_RE.match(line)
    if not m:
        return None

    raw = m.group(1)
    parts = raw.split(":")

    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        hours = 0
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
    else:
        return None

    timestamp_description = line[m.end() :].strip()
    return hours, minutes, seconds, timestamp_description


def run(channel_id: str, api_key: str, output_file: str):
    videos = []

    logger.info("Gathering uploaded videos and live streams")
    output = get_videos_in_channel(api_key=api_key, channel_id=channel_id)

    logger.info("Processing video descriptions")
    for video in output:
        video_id = video[1]
        title = video[2]
        description = video[3].split("\n")

        logger.info("Processing video: %r", title)

        found_timestamp = False
        for line in description:
            parsed = parse_timestamp(line)
            if not parsed:
                logger.debug("Skipped line (no time prefix): %r", line)
                continue

            found_timestamp = True
            hours, minutes, seconds, newline = parsed

            entry = SearchEntry(
                videoTitle=title,
                videoId=video_id,
                timestamp=Timestamp(hours=hours, minutes=minutes, seconds=seconds),
                tag="",
                line=newline,
            ).as_json_serializable()

            videos.append(entry)

        if not found_timestamp:
            logger.warning(
                "No timestamp found in description for video: %r [%s]",
                title,
                video_id,
            )

    logger.info("Serializing data to JSON format")
    dataset = json.dumps(videos)

    logger.info("Writing dataset...")
    with open(output_file, "w", encoding="utf-8") as ds:
        ds.write(dataset)

    logger.info("Dataset written to %s", output_file)
