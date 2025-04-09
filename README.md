
## Install

```
python3 -m venv env
source env/bin/activate
pip install .
```

## Commands

### Download Videos/Channels

Download any video metadata, transcripts, audio from a Youtube channel.
Requires FFMPEG to be installed.

```shell
data-pipeline download --cookies <cookiefile> https://youtube.com/channel
```

#### Cookies

If necessary, download your cookies using an extension like <https://github.com/hrdl-github/cookies-txt>
and use `--cookies` with a path to the file.

### Extract URLs

Extract any URLs found in the video descriptions to see where they link out.
Run this after downloading the video metadata above.

```shell
data-pipeline extract-urls
```

### Export Video Stats

Extract statistics about each video (channel, likes, views) and export to a CSV file
for further analysis. The data will be exported to `data/video_stats.csv`.

```shell
data-pipeline export-video-stats
```

### Generate Topics from Metadata

Use Amazon Bedrock models to extract topics from the downloaded video metadata.
Defaults to the Nova Lite model (make sure you
["enable" the model](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html) 
in your AWS account), but any Bedrock compatible model can be used.

Before running the script, set your AWS credentials in the CLI. Refer to this document for
more: <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html>

```shell
data-pipeline generate-topics \
    --region <aws-region> \
    --model-id <bedrock-model>
```