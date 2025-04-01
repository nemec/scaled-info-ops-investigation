import argparse
import logging
import pathlib

import rich.logging

from .commands import download_channels, generate_topics, extract_urls, export_stats

try:
    from .commands.audio_transcriber import transcribe_audio
    supports_transcription = True
except ImportError:
    transcribe_audio = None
    supports_transcription = False
from .constants import DEFAULT_DATA_DIR
from .models import Args, DownloaderArgs, TopicGenerationArgs

logger = logging.getLogger(__name__)


def temperature(arg) -> float:
    try:
        f = float(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be a floating point number.")
    if f < 0.0 or f > 1.0:
        raise argparse.ArgumentTypeError("Must be between 0 and 1 (inclusive).")
    return f


def main():
    parser = argparse.ArgumentParser()

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--data-dir', default=DEFAULT_DATA_DIR, type=pathlib.Path)
    base_parser.add_argument('--debug', action='store_true')

    sp = parser.add_subparsers(dest='command')

    dl_p = sp.add_parser('download', parents=[base_parser],
                         help="Download audio and metadata from Youtube channels")
    dl_p.add_argument('--cookies', type=pathlib.Path,
                      help="A file containing browser cookies for your Youtube session in 'Netscape' format. "
                           "Only necessary if Youtube throttles you unnecessarily. "
                           "Browser extensions can help you download your cookies in this format.")
    dl_p.add_argument('--wait', type=int, default=1,
                      help="Time, in seconds, to wait between downloads. Transcripts are throttled heavily.")
    dl_p.add_argument('channel_urls', nargs='+',
                      help="A list of Youtube channel URLs to download content from")

    tg_p = sp.add_parser('generate-topics', parents=[base_parser],
                         help="Generate topics from already downloaded Youtube channel metadata")
    tg_p.add_argument('--region', type=str,
                      help="AWS region")
    tg_p.add_argument('--model-id', type=str, default="amazon.nova-lite-v1:0",
                      help="Amazon bedrock Model ID. You must have 'requested' this model in your AWS account.")
    tg_p.add_argument('--temperature', type=temperature, default=0.5,
                      help="LLM temperature value to set on the model")

    sp.add_parser('extract-urls', parents=[base_parser],
                  help="Extract unique URLs from Youtube video descriptions")

    sp.add_parser('export-video-stats', parents=[base_parser],
                  help="Export statistics on the collected videos")

    if supports_transcription:
        sp.add_parser('transcribe-audio', parents=[base_parser],
                      help="Transcribe audio from already downloaded Youtube channel audio")

    # noinspection PyTypeChecker
    args: Args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich.logging.RichHandler(markup=True)]
    )
    if args.debug:
        logging.getLogger("data_pipeline").setLevel(logging.DEBUG)

    if not args.data_dir.exists():
        args.data_dir.mkdir()

    if args.command == 'download':
        args: DownloaderArgs
        download_channels(args)
    elif args.command == 'generate-topics':
        args: TopicGenerationArgs
        generate_topics(args)
    elif args.command == 'transcribe-audio':
        args: Args
        transcribe_audio(args)
    elif args.command == 'extract-urls':
        extract_urls(args)
    elif args.command == 'export-video-stats':
        export_stats(args)
