from unittest.mock import patch

from yt_crawl.youtube_api import get_upload_playlist_id, get_videos_in_channel


def test_get_upload_playlist_id():
    response = {
        "items": [
            {"contentDetails": {"relatedPlaylists": {"uploads": "UPLOADS_PLAYLIST_ID"}}}
        ]
    }

    with patch("yt_crawl.youtube_api._get", return_value=response):
        assert get_upload_playlist_id("api123", "channel123") == "UPLOADS_PLAYLIST_ID"


def test_get_videos_in_channel_paginates():
    first = {
        "items": [
            {
                "snippet": {
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "resourceId": {"videoId": "vid1"},
                    "title": "Video One",
                    "description": "desc1",
                }
            }
        ],
        "nextPageToken": "TOKEN",
    }
    second = {
        "items": [
            {
                "snippet": {
                    "publishedAt": "2024-01-02T00:00:00Z",
                    "resourceId": {"videoId": "vid2"},
                    "title": "Video Two",
                    "description": "desc2",
                }
            }
        ]
    }

    with (
        patch("yt_crawl.youtube_api.get_upload_playlist_id", return_value="UPLOADS"),
        patch("yt_crawl.youtube_api._get", side_effect=[first, second]),
    ):
        videos = get_videos_in_channel("api123", "channel123")

    assert videos == [
        ["2024-01-01T00:00:00Z", "vid1", "Video One", "desc1"],
        ["2024-01-02T00:00:00Z", "vid2", "Video Two", "desc2"],
    ]
