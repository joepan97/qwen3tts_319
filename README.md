# Qwen3-TTS 本地工具包

這是一個可在 **macOS、Linux、Linux + NVIDIA GPU** 使用的 Qwen3-TTS 本地工具包，提供：

- CLI 指令產生語音
- 本機 WebUI
- 本機 HTTP API
- WAV / OGG / MP3 輸出
- 語速控制
- 繁體中文自動轉簡體中文後再合成
- 中文口氣說明欄位
- WebUI 口氣選項下拉選單
- CPU / CUDA 可配置

這個專案主要設計給本地個人使用，以及 Qwen3-TTS 的本地測試與包裝。

## 功能特色

- **CLI 包裝器**：可用 `./serena-tts` 直接從 shell 產生語音
- **WebUI**：本機瀏覽器介面，預設 `http://127.0.0.1:7860`
- **API 伺服器**：本機 HTTP API，預設 `http://127.0.0.1:7861`
- **音檔格式**：支援 `.wav`、`.ogg`、`.mp3`
- **語速控制**：`0.5x` 到 `1.5x`
- **口氣控制**：透過自然語言 instruction 指定情緒 / 口氣
- **口氣選項**：自然 / 溫柔 / 生氣 / 難過 / 開朗 / 嚴肅 / 播報 / 故事
- **檔案操作輔助**：最新檔案路徑、輸出資料夾路徑、打開資料夾、選取最新檔案
- **較清楚的錯誤訊息**：WebUI 會把常見錯誤翻成比較容易理解的說明
- **跨平台啟動腳本**：`start-webui` / `start-api` 可在 macOS、Linux 使用
- **NVIDIA GPU 支援**：可透過環境變數指定 `cuda:0`、`float16`、`flash_attention_2`

## 已測試 / 設計目標

- macOS（Apple Silicon）
- Linux 相容啟動流程已整理完成
- Linux + NVIDIA GPU 可配置模式已加入
- Python 3.11
- `qwen-tts`
- 模型：`Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`

## 專案結構

```text
qwen3-tts/
├── .gitignore
├── README.md
├── README.local.md
├── INSTALL-QWEN3-TTS.md
├── requirements.txt
├── requirements-cuda.txt
├── serena_tts.py        # Python 語音合成包裝
├── diagnose-env.py      # 檢查 torch / CUDA / ffmpeg / sox 狀態
├── install-ubuntu-nvidia.sh
├── Dockerfile.cuda
├── serena-tts           # shell 指令包裝
├── tts_service.py       # 共用的生成 / 轉檔 / 路徑邏輯
├── webui.py             # 本地 Gradio WebUI
├── api_server.py        # 本地 FastAPI 伺服器
├── start-webui          # 啟動 WebUI
├── start-api            # 啟動 API 伺服器
├── call-tts-api         # 從 shell 呼叫 API
├── smoke_test.py
├── compare_speakers.py
└── out/                 # 生成的音檔（已忽略）
```

## 安裝方式

### 1. 建立 Python 虛擬環境

```bash
cd qwen3-tts
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

### 2. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

## 系統依賴

### macOS

```bash
brew install ffmpeg sox
```

### Ubuntu / Debian（CPU）

```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg sox
```

### Ubuntu / Debian（NVIDIA）

除了上面的系統依賴外，還需要：

- NVIDIA Driver
- CUDA 可用環境
- 與你 CUDA 版本相容的 PyTorch

如果你使用 NVIDIA，通常建議先依 PyTorch 官方文件安裝對應 CUDA 版本的 `torch` / `torchaudio`。

也可以先用專案內附腳本協助準備環境：

```bash
chmod +x install-ubuntu-nvidia.sh
./install-ubuntu-nvidia.sh
```

> 注意：腳本裡仍保留了 PyTorch CUDA 安裝提示，實際使用時請依你的 CUDA 版本替換成官方建議指令。

## 使用方式

### CLI：直接產生語音

```bash
cd qwen3-tts
./serena-tts '你好，這是一段測試。'
```

### 啟動 WebUI

```bash
cd qwen3-tts
./start-webui
```

然後打開：

```text
http://127.0.0.1:7860
```

### 啟動 API 伺服器

```bash
cd qwen3-tts
./start-api
```

健康檢查：

```bash
curl http://127.0.0.1:7861/health
```

### 從 shell 呼叫 API

```bash
cd qwen3-tts
./call-tts-api '你好，這是 API 測試。'
```

## 裝置 / dtype / NVIDIA 設定

這個版本支援用環境變數控制推理裝置：

### 可用環境變數

- `QWEN_TTS_DEVICE`
  - `auto`
  - `cpu`
  - `cuda:0`
- `QWEN_TTS_DTYPE`
  - `auto`
  - `float32`
  - `float16`
  - `bfloat16`
- `QWEN_TTS_FLASH_ATTN`
  - `auto`
  - `on`
  - `off`

### 預設行為

- `QWEN_TTS_DEVICE=auto`
  - 有 CUDA 時優先用 `cuda:0`
  - 否則 fallback 到 `cpu`
- `QWEN_TTS_DTYPE=auto`
  - CUDA：預設 `float16`
  - CPU：預設 `float32`
- `QWEN_TTS_FLASH_ATTN=auto`
  - CUDA：預設嘗試 `flash_attention_2`
  - CPU：不使用

### Linux + NVIDIA 範例

```bash
export QWEN_TTS_DEVICE=cuda:0
export QWEN_TTS_DTYPE=float16
export QWEN_TTS_FLASH_ATTN=auto
./start-webui
```

如果你想保守一點，也可以：

```bash
export QWEN_TTS_DEVICE=cuda:0
export QWEN_TTS_DTYPE=float16
export QWEN_TTS_FLASH_ATTN=off
./start-webui
```

### 環境診斷

你可以用這個腳本檢查目前環境是否真的看得到 CUDA：

```bash
python diagnose-env.py
```

它會輸出：
- Python 版本
- torch 版本
- `torch.cuda.is_available()`
- GPU 張數
- GPU 名稱
- ffmpeg / sox 是否存在
- 目前相關環境變數

## WebUI 說明

WebUI 目前支援：

- **文字**：要朗讀的內容
- **Speaker**：目前測過的 speaker
- **Language**：合成語言
- **語調 / 風格預設**：生成參數預設
- **口氣選項**：快速選擇口氣風格
- **口氣說明（中文）**：自訂中文口氣 instruction
- **語速**：播放速度調整
- **輸出資訊 / 錯誤訊息**：結果資訊或較清楚的失敗原因

### 口氣選項

目前提供：

- 自訂
- 自然
- 溫柔
- 生氣
- 難過
- 開朗
- 嚴肅
- 播報
- 故事

選擇口氣選項後，會自動把對應中文 instruction 帶入「口氣說明（中文）」欄位；你也可以再手動修改。

## API 說明

### `GET /health`

```json
{"ok": true}
```

### `GET /meta`

回傳支援的 speakers、languages、presets。

### `GET /latest`

回傳最近生成的檔案列表。

### `POST /synthesize`

請求範例：

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

## Linux / 跨平台說明

這個版本已經去掉以下平台綁定：

- 寫死的 Homebrew `ffmpeg` 路徑
- 核心邏輯裡只能用 macOS `open`
- 寫死的 macOS 絕對啟動路徑
- 寫死只能用 CPU 的模型載入方式

目前行為：

- `ffmpeg` 會從 `PATH` 自動尋找
- 也可以用 `QWEN_TTS_FFMPEG` 手動指定
- 開資料夾 / 選檔案時：
  - macOS 用 `open`
  - Linux 用 `xdg-open`
- 如果 Linux 沒有 GUI opener，也不影響主要 TTS 功能，只是不能自動打開資料夾

## 注意事項

- 這個專案使用的是 **instruction-based tone control**，不是結構化的 `emotion=` API
- 繁體中文輸入可先自動轉成簡體中文，以提高 Qwen3-TTS 辨識與發音穩定度
- 生成音檔預設不加入 git
- `.venv`、`out/`、`speaker-tests/` 等本地產物都應忽略
- NVIDIA 模式要先有正確的 PyTorch + CUDA 安裝，不是只設環境變數就一定能跑

## 常用指令

```bash
source .venv/bin/activate
python smoke_test.py
python compare_speakers.py
python diagnose-env.py
./start-webui
./start-api
```

## Docker（CUDA 範例）

專案內有一份 `Dockerfile.cuda` 可作為 Linux + NVIDIA 的起點。

建置：

```bash
docker build -f Dockerfile.cuda -t qwen3tts-cuda .
```

執行（需搭配 NVIDIA Container Toolkit）：

```bash
docker run --rm --gpus all -p 7860:7860 -p 7861:7861 qwen3tts-cuda
```

> 注意：`Dockerfile.cuda` 內的 torch 安裝行是示例，實際仍應依你的 CUDA / 驅動版本調整。

## 授權提醒

如果你要把這個專案做公開散佈或部署，請另外確認上游 `qwen-tts` 與模型本身的授權條款。
