import pytest
from unittest.mock import patch

from yt_crawl.cli import cli


def test_cli_accepts_multiple_channel_ids():
    with (
        patch("yt_crawl.cli.run") as mock_run,
        patch("yt_crawl.cli.os.getenv", return_value="api123"),
        patch("sys.argv", ["prog", "-c", "channel123", "-c", "channel456"]),
    ):
        cli()

    mock_run.assert_called_once_with(
        ["channel123", "channel456"],
        "api123",
        "dataset.json",
    )


def test_cli_uses_output_file_and_api_key():
    with (
        patch("yt_crawl.cli.run") as mock_run,
        patch(
            "sys.argv", ["prog", "-c", "channel123", "-a", "api123", "-o", "out.json"]
        ),
    ):
        cli()

    mock_run.assert_called_once_with(
        ["channel123"],
        "api123",
        "out.json",
    )


def test_cli_exits_when_api_key_missing():
    with (
        patch("yt_crawl.cli.run") as mock_run,
        patch("yt_crawl.cli.os.getenv", return_value=None),
        patch("sys.argv", ["prog", "-c", "channel123"]),
    ):
        with pytest.raises(SystemExit) as exc:
            cli()

    assert exc.value.code == 1
    mock_run.assert_not_called()
