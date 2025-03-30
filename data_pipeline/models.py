import pathlib
from typing import List


class Args:
    command: str
    data_dir: pathlib.Path
    debug: bool


class DownloaderArgs(Args):
    cookies: pathlib.Path
    wait: int
    channel_urls: List[str]


class TopicGenerationArgs(Args):
    region: str
    model_id: str
    temperature: float
