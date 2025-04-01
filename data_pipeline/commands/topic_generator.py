import csv
from datetime import datetime
import json
import logging
import pathlib
import time
from typing import Set

import boto3
import botocore.exceptions

from ..constants import VIDEO_SUBDIR
from ..guardrails import (
    SufficientTextGuardrail,
    TranslatedGuardrail,
    PreambleGuardrail,
    OutputFormatCheckerGuardrail,
    InvalidLlmInputException,
    InvalidLlmResponseException,
    NotTranslatedLlmResponseException,
)
from ..models import TopicGenerationArgs
from ..utils import pre_process_description, post_process_topic

logger = logging.getLogger(__name__)


def _get_existing_video_ids(csv_file: pathlib.Path) -> Set[str]:
    seen = set()
    with open(csv_file, 'r') as output_csv:
        reader = csv.reader(output_csv)
        next(reader, None)
        for row in reader:
            seen.add(row[0])
    return seen


PROMPT = """
Identify the top three topics of the following text, translated into English and separated by line breaks. 
Keep the topic names short. Do not include a preamble such as "certainly...".
Text:
"""

SYSTEM_PROMPT = """You are an assistant that identifies the top three topics of a user's text, translated into English.
Return those three topics in your response separated by line breaks. Do not include extra information before
or after the topics. Do not number or mark the topics with bullets."""


def generate_topics(args: TopicGenerationArgs):
    input_guardrails = [
        SufficientTextGuardrail()
    ]
    output_guardrails = [
        TranslatedGuardrail(),
        PreambleGuardrail(),
        OutputFormatCheckerGuardrail(3),
    ]

    client_args = {}
    if args.region is not None:
        client_args['region_name'] = args.region
    client = boto3.client("bedrock-runtime", **client_args)
    csv_file = args.data_dir / 'topics.csv'
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
                "topic"
            ])
        for idx, file in enumerate(pathlib.Path(args.data_dir / VIDEO_SUBDIR).glob("**/*.info.json")):
            if (idx + 1) % 100 == 0:
                logger.info(f"Processing {idx}")
            with open(file, "r") as f:
                data = json.load(f)
                if data['id'] in seen:
                    logger.info(f"skipping {data['id']}, already processed")
                    continue
                if 'timestamp' not in data:
                    logger.info(f"Skipping {data['id']} because it has no timestamp")
                    continue
                desc = data.get('fulltitle', data.get('title')) + '\n' + data.get("description")
                if not desc:
                    logger.info(f"Skipping {data['id']} because it has no description")
                passed_guardrails = True
                for guardrail in input_guardrails:
                    try:
                        guardrail.evaluate(desc)
                    except InvalidLlmInputException as e:
                        logger.error(f"Skipping {data['id']} because it has an invalid LLM input: {e}")
                        passed_guardrails = False
                        break
                if not passed_guardrails:
                    continue

                desc = pre_process_description(desc)
                conversation = [
                    {
                        "role": "user",
                        "content": [{"text": desc}],
                    }
                ]
                content: str | None = None
                response = None
                tries = 2
                while response is None and tries > 0:
                    try:
                        response = client.converse(
                            modelId=args.model_id,
                            messages=conversation,
                            system=[{"text": SYSTEM_PROMPT}],
                            inferenceConfig={
                                "maxTokens": 512,
                                "temperature": args.temperature,
                                "topP": 0.9
                            },
                        )
                        pending_content: str = response['output']['message']['content'][0]['text']
                        logger.debug(f"Response before processing guardrails: {pending_content}")
                        for guardrail in output_guardrails:
                            guardrail.evaluate(pending_content)
                        content = pending_content
                    except botocore.exceptions.ClientError as e:
                        response = None
                        logger.info(f"caught exception {e.__class__.__name__}, retrying...")
                        time.sleep(1)
                        tries -= 1
                    except NotTranslatedLlmResponseException:
                        response = None
                        logger.warning("Received a non-English response. Attempting to redirect...")
                        # Continue the conversation and add a request to LLM to fix the previous response
                        conversation.extend([
                            {
                                "role": "assistant",
                                "content": [{"text": pending_content}],
                            },
                            {
                                "role": "user",
                                "content": [{"text": "The previous response was not translated into English. "
                                                     "Please only give English topics."}],
                            }
                        ])
                        time.sleep(1)
                        tries -= 1
                    except InvalidLlmResponseException as e:
                        response = None
                        logger.error(f"Received an invalid LLM response: {e}, retrying...")
                        time.sleep(1)
                        tries -= 1
                if content is None:
                    logger.error(f"Failed to get output for video {data['id']} after retries, skipping.")
                    continue

                topics = [line.strip() for line in content.splitlines() if len(line.strip()) > 0]
                ts = datetime.fromtimestamp(data['timestamp'])
                for topic in topics:
                    processed_topic = post_process_topic(topic)
                    channel_name = data.get('channel', data.get('uploader', '<missing>'))
                    view_count = data.get('view_count', -1)
                    like_count = data.get('like_count', -1)
                    duration = data.get('duration', -1)
                    writer.writerow([
                        data['id'], data['channel_id'], channel_name,
                        ts.year, ts.month, ts.day, data['timestamp'],
                        view_count, like_count, duration,
                        processed_topic])
