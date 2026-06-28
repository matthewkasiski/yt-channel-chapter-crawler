import argparse
import logging
import os

from .crawler import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def build_parser():
    parser = argparse.ArgumentParser(description="Generate the dataset for the web app")
    parser.add_argument(
        "-c",
        "--yt_channel_id",
        required=True,
        action="append",
        help="YouTube Channel ID to parse (can be provided multiple times)",
    )
    parser.add_argument(
        "-a",
        "--yt_api_key",
        default=os.getenv("YT_CRAWL_YT_API_KEY"),
        required=False,
        help="Google API key; can also be set via YT_CRAWL_YT_API_KEY",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        default="dataset.json",
        help="Output JSON file path",
    )
    return parser


def cli():
    args = build_parser().parse_args()

    if not args.yt_api_key:
        logger.error("No API key (-a) provided")
        raise SystemExit(1)

    run(args.yt_channel_id, args.yt_api_key, args.output_file)


if __name__ == "__main__":
    cli()
