

## Install Instructions

```shell
git submodule add https://github.com/deepseek-ai/Janus
git submodule add https://github.com/deepseek-ai/DeepSeek-V3
python -m venv env
source env/bin/activate
cd Janus
pip install build
# Generate Janus wheel file
python -m build
cd ../DeepSeek-V3
python -m build
cd ..
pip install -e .[dev]
huggingface-cli download --local-dir data/models/deepseek deepseek-ai/DeepSeek-V3
pip install "sglang[all]>=0.4.3" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python
```
## Running

```shell
main <youtube_channel_url>
```

```shell
python3 -m sglang.launch_server --model-path data/models/deepseek --tp 8 --trust-remote-code
```

### Cookies

If necessary, download your cookies using an extension like <https://github.com/hrdl-github/cookies-txt>
and use `--cookies` with a path to the file.
