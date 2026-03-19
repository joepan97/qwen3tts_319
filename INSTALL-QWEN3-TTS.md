# Qwen3-TTS 安裝教學（Joe 的 Mac mini 實測版）

> 環境：Apple Mac mini (M1 / 16GB RAM / macOS arm64)
> 目標：安裝 Qwen3-TTS，完成本地中文 TTS 測試，並建立 Serena 語音包裝腳本。

## 一、這次做了什麼

本次安裝與驗證包含：

1. 備份 OpenClaw 設定到 `/Users/joepan/backup`
2. 在 workspace 建立獨立目錄 `qwen3-tts`
3. 用 Python 3.11 + `uv` 建立隔離虛擬環境
4. 安裝 `qwen-tts`
5. 安裝系統依賴 `sox`
6. 下載並測試 `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`
7. 比較 3 個 speaker：`serena`、`vivian`、`ono_anna`
8. 建立本地 Serena TTS 指令：`./serena-tts`
9. 讓輸出同時產生：
   - `.wav`
   - Telegram 比較友善的 `.ogg` / Opus

---

## 二、目錄位置

安裝目錄：

```bash
/Users/joepan/.openclaw/workspace/qwen3-tts
```

主要檔案：

- `.venv/`：Python 虛擬環境
- `smoke_test.py`：基本測試腳本
- `compare_speakers.py`：speaker 比較腳本
- `serena_tts.py`：Serena TTS Python 腳本
- `serena-tts`：懶人包裝指令
- `speaker-tests/`：speaker 測試輸出
- `out/`：正式 Serena 輸出目錄

---

## 三、前置需求

### 1. Homebrew
需要可用的 Homebrew：

```bash
brew --version
```

### 2. Python 3.11
建議不要用 macOS 系統內建 Python 3.9，改用 Homebrew 的 Python 3.11。

確認：

```bash
/opt/homebrew/bin/python3.11 --version
```

### 3. uv
用來建立虛擬環境：

```bash
/opt/homebrew/bin/uv --version
```

如果沒有，可安裝：

```bash
brew install uv
```

---

## 四、建立環境

### 1. 建立目錄

```bash
mkdir -p /Users/joepan/.openclaw/workspace/qwen3-tts
cd /Users/joepan/.openclaw/workspace/qwen3-tts
```

### 2. 建立虛擬環境

```bash
/opt/homebrew/bin/uv venv --python /opt/homebrew/bin/python3.11 .venv
```

### 3. 啟用虛擬環境

```bash
source .venv/bin/activate
```

### 4. 確認 pip

```bash
python -m ensurepip --upgrade
python -m pip --version
```

---

## 五、安裝 Qwen3-TTS

### 1. 更新打包工具

```bash
python -m pip install -U pip setuptools wheel
```

### 2. 安裝 qwen-tts

```bash
python -m pip install -U qwen-tts
```

安裝完成後，可確認：

```bash
python -m pip show qwen-tts torch torchaudio transformers
```

這次實測安裝到的主要版本：

- `qwen-tts 0.1.1`
- `torch 2.10.0`
- `torchaudio 2.10.0`
- `transformers 4.57.3`

---

## 六、安裝系統依賴

Qwen3-TTS 這次在本機測試時，缺少 SoX 會出現問題，所以要補上：

```bash
brew install sox
```

檢查：

```bash
/opt/homebrew/bin/sox --version
```

另外這次有用到 `ffmpeg` 轉成 Telegram 比較友善的 OGG / Opus。

檢查：

```bash
/opt/homebrew/bin/ffmpeg -version
```

如果沒有：

```bash
brew install ffmpeg
```

---

## 七、第一次測試（0.6B CustomVoice）

本次測試模型：

```bash
Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
```

建立最小測試腳本 `smoke_test.py`，用 CPU + float32 載入模型並輸出 wav。

執行：

```bash
cd /Users/joepan/.openclaw/workspace/qwen3-tts
source .venv/bin/activate
export PATH="/opt/homebrew/bin:$PATH"
python smoke_test.py
```

這次實測結果：

- 模型載入：`58.48s`
- 第一次合成：`19.82s`
- 輸出：`smoke-test.wav`

---

## 八、speaker 比較

本次測試 3 個 speaker：

- `serena`
- `vivian`
- `ono_anna`

執行：

```bash
python compare_speakers.py
```

輸出檔案：

- `speaker-tests/serena.wav`
- `speaker-tests/vivian.wav`
- `speaker-tests/ono_anna.wav`

主觀結果：

- **serena**：最適合當助理語音
- `vivian`：也不錯，但個性稍微更明顯
- `ono_anna`：有特色，但不一定最泛用

最後選定：

- **預設 voice = serena**

---

## 九、建立 Serena 懶人指令

### 1. Python 腳本
`serena_tts.py`

功能：

- 固定用 Qwen3-TTS 0.6B
- 預設 speaker = `serena`
- 讀入文字
- 產出 wav

### 2. shell 包裝腳本
`serena-tts`

功能：

- 呼叫 `serena_tts.py`
- 自動把 wav 轉成 `.ogg` / Opus
- 輸出路徑印在終端機上

執行方式：

```bash
cd /Users/joepan/.openclaw/workspace/qwen3-tts
./serena-tts '你好，這是一段 Serena 的測試。'
```

輸出範例：

```bash
WAV=/Users/joepan/.openclaw/workspace/qwen3-tts/out/serena-20260319-175155.wav
OGG=/Users/joepan/.openclaw/workspace/qwen3-tts/out/serena-20260319-175155.ogg
```

---

## 十、給 Telegram 用的格式

這次採用：

- wav：本地保存
- ogg / opus：Telegram 比較友善

轉檔方式：

```bash
ffmpeg -y -i input.wav -c:a libopus -b:a 48k output.ogg
```

實測輸出可正常送到 Telegram 作為語音訊息。

---

## 十一、目前的限制

### 1. 速度不快
這台是：

- Apple M1
- 16GB RAM
- CPU 路線

所以定位是：

- 偶爾 TTS
- 本地語音橋接
- 不適合期待超即時秒回

### 2. 不是 OpenClaw 內建 provider
OpenClaw 本身有內建 TTS，但支援的是：

- OpenAI
- ElevenLabs
- Edge TTS

Qwen3-TTS 目前是以**本地橋接腳本**方式接入，不是 OpenClaw 原生 provider。

### 3. Hugging Face 快取會佔空間
這次實測快取約：

```bash
~/.cache/huggingface
```

大小大概到數 GB 等級。

---

## 十二、我會建議的使用方式

如果你只是要：

- 偶爾產出語音
- 請 OpenClaw 用 Serena 回一段

那目前這套已經夠用。

如果你之後要：

- 更快的語音回覆
- 更穩定常駐
- 更像原生整合

可以再考慮：

1. 做常駐服務避免每次重載模型
2. 改用更適合推理的機器
3. 做成更完整的 OpenClaw plugin / provider

---

## 十三、常用指令整理

進入目錄：

```bash
cd /Users/joepan/.openclaw/workspace/qwen3-tts
```

啟用環境：

```bash
source .venv/bin/activate
export PATH="/opt/homebrew/bin:$PATH"
```

基本測試：

```bash
python smoke_test.py
```

speaker 比較：

```bash
python compare_speakers.py
```

用 Serena 產語音：

```bash
./serena-tts '你好，這是一段 Serena 的測試。'
```

---

## 十四、這次相關 commit

- `cdbd80d` — Add Qwen3-TTS local test scripts
- `c321cea` — Add Serena TTS wrapper script
- `9e740c4` — Record Serena as preferred local TTS voice

---

## 十五、結論

這次在 Joe 的 Mac mini 上，**Qwen3-TTS 0.6B 已成功安裝、測試並可實際輸出 Serena 語音**。

雖然速度不算快，但對「偶爾 TTS」與「本地語音橋接」這個目標來說，已經是可用狀態。
