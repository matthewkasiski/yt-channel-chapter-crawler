import json
from unittest.mock import mock_open, patch

from yt_ccc.crawler import parse_timestamp, run


def test_parse_timestamp_mm_ss():
    assert parse_timestamp("01:02 intro") == (0, 1, 2, "intro")


def test_parse_timestamp_hh_mm_ss():
    assert parse_timestamp("01:02:03 intro") == (1, 2, 3, "intro")


def test_run_extracts_timestamped_lines_and_writes_json():
    videos = [
        [
            "2024-01-01T00:00:00Z",
            "vid1",
            "Video One",
            "00:01 intro\n01:02:03 main topic\nnot a timestamp",
        ],
    ]

    with (
        patch("yt_ccc.crawler.get_videos_in_channel", return_value=videos),
        patch("builtins.open", mock_open()) as m,
    ):
        run(["channel123"], "api123", "out.json")

    m.assert_called_once_with("out.json", "w", encoding="utf-8")
    written = "".join(call.args[0] for call in m().write.call_args_list)
    data = json.loads(written)

    assert data == [
        {
            "videoTitle": "Video One",
            "videoId": "vid1",
            "timestamp": {"hours": 0, "minutes": 0, "seconds": 1},
            "tag": "",
            "line": "intro",
        },
        {
            "videoTitle": "Video One",
            "videoId": "vid1",
            "timestamp": {"hours": 1, "minutes": 2, "seconds": 3},
            "tag": "",
            "line": "main topic",
        },
    ]


def test_run_processes_multiple_channels():
    videos_channel_1 = [
        [
            "2024-01-01T00:00:00Z",
            "vid1",
            "Video One",
            "00:01 intro",
        ],
    ]
    videos_channel_2 = [
        [
            "2024-01-02T00:00:00Z",
            "vid2",
            "Video Two",
            "00:02 second intro",
        ],
    ]

    with (
        patch(
            "yt_ccc.crawler.get_videos_in_channel",
            side_effect=[videos_channel_1, videos_channel_2],
        ) as mock_get,
        patch("builtins.open", mock_open()) as m,
    ):
        run(["channel123", "channel456"], "api123", "out.json")

    assert mock_get.call_count == 2
    mock_get.assert_any_call(api_key="api123", channel_id="channel123")
    mock_get.assert_any_call(api_key="api123", channel_id="channel456")

    m.assert_called_once_with("out.json", "w", encoding="utf-8")
    written = "".join(call.args[0] for call in m().write.call_args_list)
    data = json.loads(written)

    assert data == [
        {
            "videoTitle": "Video One",
            "videoId": "vid1",
            "timestamp": {"hours": 0, "minutes": 0, "seconds": 1},
            "tag": "",
            "line": "intro",
        },
        {
            "videoTitle": "Video Two",
            "videoId": "vid2",
            "timestamp": {"hours": 0, "minutes": 0, "seconds": 2},
            "tag": "",
            "line": "second intro",
        },
    ]


def test_run_warns_when_no_timestamp_found():
    videos = [
        [
            "2024-01-01T00:00:00Z",
            "vid1",
            "Video One",
            "no timestamps here",
        ],
    ]

    with (
        patch("yt_ccc.crawler.get_videos_in_channel", return_value=videos),
        patch("builtins.open", mock_open()),
        patch("yt_ccc.crawler.logger.warning") as mock_warning,
    ):
        run(["channel123"], "api123", "out.json")

    mock_warning.assert_called_once()
