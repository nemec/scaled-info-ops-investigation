import csv
import json
import logging
import pathlib
from datetime import datetime
from typing import Set

from ..constants import VIDEO_SUBDIR
from ..models import Args

logger = logging.getLogger(__name__)


def _get_existing_video_ids(csv_file: pathlib.Path) -> Set[str]:
    seen = set()
    with open(csv_file, 'r') as output_csv:
        reader = csv.reader(output_csv)
        next(reader, None)
        for row in reader:
            seen.add(row[0])
    return seen


def export_stats(args: Args) -> None:
    csv_file = args.data_dir / 'video_stats.csv'
    logger.info(f"Writing stats to {csv_file}")
    csv_file_exists = csv_file.exists()
    if csv_file_exists:
        seen = _get_existing_video_ids(csv_file)
    else:
        seen = set()
    with open(csv_file, 'a') as output_csv:
        writer = csv.writer(output_csv)
        if not csv_file_exists:
            writer.writerow([
                "id", "channel_id", "channel_name",
                "year", "month", "day", "timestamp",
                "view_count", "like_count", "duration",
            ])
        for idx, file in enumerate(pathlib.Path(args.data_dir / VIDEO_SUBDIR).glob("**/*.info.json")):
            if idx != 0 and idx % 1000 == 0:
                logger.info(f"Processing {idx}")
            with open(file, "r") as f:
                data = json.load(f)
                if data['id'] in seen:
                    logger.info(f"skipping {data['id']}, already processed")
                    continue
                if 'timestamp' not in data:
                    logger.info(f"Skipping {data['id']} because it has no timestamp")
                    continue

                ts = datetime.fromtimestamp(data['timestamp'])
                channel_name = data.get('channel', data.get('uploader', '<missing>'))
                view_count = data.get('view_count', -1)
                like_count = data.get('like_count', -1)
                duration = data.get('duration', -1)
                writer.writerow([
                    data['id'], data['channel_id'], channel_name,
                    ts.year, ts.month, ts.day, data['timestamp'],
                    view_count, like_count, duration
                ])
