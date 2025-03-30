import json

import rich

from ..models import Args
from ..utils import find_urls_in_text


def extract_urls(args: Args):
    urls = set()
    for file_path in (args.data_dir / 'videos').glob('**/*.info.json'):
        with open(file_path, 'r') as f:
            info_json = json.load(f)
        description = info_json['description']
        for url in find_urls_in_text(description):
            if url not in urls:
                rich.print(url)
            urls.add(url)
