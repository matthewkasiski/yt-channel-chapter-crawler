from yt_crawl.models import SearchEntry, Timestamp


def test_search_entry_serializes():
    entry = SearchEntry(
        videoTitle="My Video",
        videoId="abc123",
        timestamp=Timestamp(hours=1, minutes=2, seconds=3),
        tag="foo",
        line="hello world",
    )

    assert entry.as_json_serializable() == {
        "videoTitle": "My Video",
        "videoId": "abc123",
        "timestamp": {"hours": 1, "minutes": 2, "seconds": 3},
        "tag": "foo",
        "line": "hello world",
    }
