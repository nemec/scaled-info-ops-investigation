import logging
from typing import List
import shutil

import yt_dlp

from ..constants import VIDEO_SUBDIR
from ..models import DownloaderArgs

logger = logging.getLogger(__name__)


def download_channels(args: DownloaderArgs) -> None:
    if shutil.which('ffmpeg') is None:
        logger.error("ffmpeg not found. Please install ffmpeg.")
        return

    downloaded_video_infos: List[dict] = []

    def progress_callback(video_data):
        if video_data['status'] == 'finished':
            downloaded_video_infos.append(video_data.get('info_dict'))

    ydl_opts = {
        'writeinfojson': 'true',
        'writesubtitles': 'true',
        'writeautomaticsub': 'true',
        'sleep_interval': args.wait,
        'sleep_interval_subtitles': args.wait,
        'download_archive': str(args.data_dir / 'download_archive.txt'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': (f'{args.data_dir}/{VIDEO_SUBDIR}/%(channel_id)s/'
                    f'%(upload_date>%Y-%m-%d)s - %(id)s.%(ext)s'),
        'progress_hooks': [progress_callback],
    }
    if args.cookies:
        if not args.cookies.exists():
            logger.error("Cookies file does not exist")
            return
        ydl_opts['cookiefile'] = str(args.cookies)

    with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
        logger.info("Downloading videos")
        ytdl.download(args.channel_urls)

    logger.info("Downloaded %d videos", len(downloaded_video_infos))
