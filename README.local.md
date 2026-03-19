# Qwen3-TTS local notes

Local install for Joe's Mac mini.

## Environment
- Python venv: `qwen3-tts/.venv`
- Model tested: `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`
- Device used: CPU on Apple M1

## Useful commands

Activate env:

```bash
cd /Users/joepan/.openclaw/workspace/qwen3-tts
source .venv/bin/activate
export PATH="/opt/homebrew/bin:$PATH"
```

Run one-shot smoke test:

```bash
python smoke_test.py
```

Compare three speakers:

```bash
python compare_speakers.py
```

Generate speech with Serena (outputs wav + Telegram-friendly ogg):

```bash
./serena-tts '你好，這是一段 Serena 的測試。'
```

Start local WebUI:

```bash
./start-webui
# then open http://127.0.0.1:7860
```

Start local API server:

```bash
./start-api
# API at http://127.0.0.1:7861
```

Call local API from shell:

```bash
./call-tts-api '你好，這是 API 測試。'
```

WebUI extras:
- style presets (gentle / story / slow_clear / lively / balanced)
- adjustable speaking speed (0.5x to 1.5x)
- Traditional Chinese -> Simplified Chinese conversion for Chinese synthesis
- latest generated files panel + direct download
- optional `.mp3` export in addition to `.wav` and `.ogg`

## Generated files
- `smoke-test.wav`
- `speaker-tests/serena.wav`
- `speaker-tests/vivian.wav`
- `speaker-tests/ono_anna.wav`
- `out/*.wav`
- `out/*.ogg`

These audio files are local test outputs and should not be committed.
