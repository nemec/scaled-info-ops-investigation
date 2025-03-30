import json
import logging
import pathlib

from ..constants import VIDEO_SUBDIR
from ..models import Args

import langdetect
import whisper

logger = logging.getLogger(__name__)


def transcribe_audio(args: Args) -> None:
    whisper_model = whisper.load_model("turbo")

    for file_path in (args.data_dir / VIDEO_SUBDIR).glob("**/*.mp3"):
        file_path: pathlib.Path
        with open(file_path.with_suffix(".info.json"), 'r') as f:
            info_json = json.load(f)
        logger.info(f"Processing {file_path}")
        language = langdetect.detect(info_json['description'])
        logger.info(f"Detected language: {language}")

        logger.info("Extracting transcript")
        result = whisper.transcribe(whisper_model, str(file_path), language=language)
        transcript_file = file_path.with_suffix('.transcript.txt')
        with open(transcript_file, 'w') as f:
            f.write(result['text'])
