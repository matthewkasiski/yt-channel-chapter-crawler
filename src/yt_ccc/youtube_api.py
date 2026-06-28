import requests

API_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(RuntimeError):
    pass


def _get(url, params):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_upload_playlist_id(api_key: str, channel_id: str) -> str:
    data = {"id": channel_id, "key": api_key, "part": "contentDetails"}
    response = _get(f"{API_URL}/channels", data)

    try:
        return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except (KeyError, IndexError) as e:
        raise YouTubeAPIError("Could not resolve uploads playlist for channel") from e


def get_videos_in_channel(api_key: str, channel_id: str):
    playlist_id = get_upload_playlist_id(api_key, channel_id)

    output = []
    next_page_token = None

    while True:
        data = {
            "key": api_key,
            "playlistId": playlist_id,
            "part": "snippet",
            "maxResults": "50",
        }
        if next_page_token:
            data["pageToken"] = next_page_token

        response = _get(f"{API_URL}/playlistItems", data)

        for video in response.get("items", []):
            snippet = video["snippet"]
            output.append(
                [
                    snippet.get("publishedAt"),
                    snippet["resourceId"]["videoId"],
                    snippet.get("title", ""),
                    snippet.get("description", ""),
                ]
            )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return output
