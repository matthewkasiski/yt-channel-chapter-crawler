import dataclasses


@dataclasses.dataclass
class Timestamp:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


@dataclasses.dataclass
class SearchEntry:
    videoTitle: str
    videoId: str
    timestamp: Timestamp
    tag: str
    line: str

    def as_json_serializable(self):
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
