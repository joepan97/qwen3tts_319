# Qwen3-TTS Local Toolkit

A local Qwen3-TTS toolkit for **macOS and Linux** with:

- simple CLI generation
- local WebUI
- local HTTP API
- WAV / OGG / MP3 export
- speaking speed control
- Traditional Chinese -> Simplified Chinese conversion for synthesis
- Chinese tone instruction field
- tone preset dropdown in the WebUI

This project is designed for local personal use and CPU-based testing.

## Features

- **CLI wrapper**: generate speech from shell with `./serena-tts`
- **WebUI**: browser-based local interface at `http://127.0.0.1:7860`
- **API server**: local HTTP endpoint at `http://127.0.0.1:7861`
- **Formats**: `.wav`, `.ogg`, `.mp3`
- **Speed control**: `0.5x` to `1.5x`
- **Chinese tone instructions**: natural-language instruction field for emotion / tone guidance
- **Tone presets**: Natural / Gentle / Angry / Sad / Cheerful / Serious / Broadcast / Story
- **Path helpers**: latest file path, output folder path, open folder, reveal latest file
- **Readable errors**: more understandable UI error explanations for common failures
- **Cross-platform launchers**: start scripts work on macOS and Linux

## Tested Environment

- macOS (Apple Silicon)
- Linux-compatible launch flow prepared
- Python 3.11
- `qwen-tts`
- model: `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`
- runtime: CPU

## Project Structure

```text
qwen3-tts/
├── .gitignore
├── README.md
├── README.local.md
├── INSTALL-QWEN3-TTS.md
├── serena_tts.py        # Python synthesis wrapper
├── serena-tts           # shell wrapper
├── tts_service.py       # shared generation/export logic
├── webui.py             # local Gradio WebUI
├── api_server.py        # local FastAPI server
├── start-webui          # start WebUI
├── start-api            # start API server
├── call-tts-api         # call API from shell
├── smoke_test.py
├── compare_speakers.py
└── out/                 # generated files (ignored)
```

## Installation

### Python environment

```bash
cd qwen3-tts
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

### Python packages

```bash
python -m pip install qwen-tts fastapi uvicorn gradio opencc-python-reimplemented soundfile
```

## System dependencies

### macOS

```bash
brew install ffmpeg sox
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg sox
```

If your distro uses a different package name for Python 3.11, install the matching version available on your system.

## Usage

### CLI: generate speech

```bash
cd qwen3-tts
./serena-tts '你好，這是一段測試。'
```

### Start WebUI

```bash
cd qwen3-tts
./start-webui
```

Then open:

```text
http://127.0.0.1:7860
```

### Start API server

```bash
cd qwen3-tts
./start-api
```

Health check:

```bash
curl http://127.0.0.1:7861/health
```

### Call API from shell

```bash
cd qwen3-tts
./call-tts-api '你好，這是 API 測試。'
```

## WebUI Usage

The WebUI supports:

- **文字**: text to speak
- **Speaker**: current built-in tested speakers
- **Language**: synthesis language
- **語調 / 風格預設**: generation parameter preset
- **口氣選項**: preset tone selector
- **口氣說明（中文）**: free-form Chinese tone instruction
- **語速**: playback speed adjustment
- **輸出資訊 / 錯誤訊息**: result info or readable failure reason

### Tone Presets

Available tone presets:

- 自訂
- 自然
- 溫柔
- 生氣
- 難過
- 開朗
- 嚴肅
- 播報
- 故事

Selecting a tone preset auto-fills the Chinese tone instruction field, and you can still edit it manually.

### Example tone instructions

- `請用溫柔、平靜、柔和的口氣來讀。`
- `請用生氣、不耐煩、帶有情緒的口氣來讀。`
- `請用像新聞播報一樣清楚、穩定的口氣來讀。`
- `請用像說故事一樣有畫面感、帶節奏的口氣來讀。`

## API Usage

### `GET /health`

```json
{"ok": true}
```

### `GET /meta`

Returns supported speakers, languages, and presets.

### `GET /latest`

Returns latest generated files.

### `POST /synthesize`

Example request:

```json
{
  "text": "你好，這是一段測試。",
  "speaker": "serena",
  "language": "Chinese",
  "max_new_tokens": 700,
  "export_ogg": true,
  "export_mp3": true,
  "preset": "balanced",
  "auto_t2s": true,
  "speed": 1.0,
  "instruct": "請用溫柔、平靜的口氣來讀。"
}
```

## Linux Notes

This project no longer depends on:

- hardcoded Homebrew-only `ffmpeg` paths
- macOS-only `open` commands in core logic
- absolute macOS-only startup paths

Behavior now is:

- `ffmpeg` is resolved from `PATH` (or `QWEN_TTS_FFMPEG` if set)
- folder/file opening uses:
  - `open` on macOS
  - `xdg-open` on Linux when available
- startup scripts resolve their own directory dynamically

If no GUI opener exists on Linux, the project still works; the UI will return paths even if the system cannot auto-open folders.

## Notes

- This project uses **instruction-based tone control**, not a strict structured `emotion=` API.
- Traditional Chinese input can be auto-converted to Simplified Chinese before synthesis for better recognition.
- Generated audio files are intentionally excluded from git.
- `.venv`, `out/`, `speaker-tests/`, and other local artifacts should not be committed.

## Common Local Commands

```bash
source .venv/bin/activate
python smoke_test.py
python compare_speakers.py
./start-webui
./start-api
```

## License

Check the upstream `qwen-tts` and model licenses before redistributing or deploying beyond personal/local use.
