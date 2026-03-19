#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from opencc import OpenCC

from serena_tts import synthesize, DEFAULT_LANGUAGE, DEFAULT_MAX_NEW_TOKENS, DEFAULT_SPEAKER

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "out"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
SPEAKERS = ["serena", "vivian", "ono_anna"]
LANGUAGES = ["Chinese", "English", "Japanese"]
DEFAULT_PRESET = "balanced"
DEFAULT_SPEED = 1.0

_PRESETS: Dict[str, Dict[str, object]] = {
    "balanced": {
        "label": "平衡 / 自然",
        "max_new_tokens": DEFAULT_MAX_NEW_TOKENS,
        "text_prefix": "",
    },
    "gentle": {
        "label": "溫柔 / 柔和",
        "max_new_tokens": max(DEFAULT_MAX_NEW_TOKENS + 128, 768),
        "text_prefix": "請用溫柔、自然、放鬆的語氣朗讀：",
    },
    "story": {
        "label": "說故事 / 旁白感",
        "max_new_tokens": max(DEFAULT_MAX_NEW_TOKENS + 192, 896),
        "text_prefix": "請用有節奏、帶一點故事感的旁白語氣朗讀：",
    },
    "slow_clear": {
        "label": "慢速 / 清楚",
        "max_new_tokens": max(DEFAULT_MAX_NEW_TOKENS + 256, 960),
        "text_prefix": "請放慢速度、咬字清楚、停頓自然地朗讀：",
    },
    "lively": {
        "label": "活潑 / 聊天感",
        "max_new_tokens": max(DEFAULT_MAX_NEW_TOKENS + 96, 768),
        "text_prefix": "請用比較活潑、像聊天一樣自然的語氣朗讀：",
    },
}

_cc_t2s = OpenCC("t2s")


def preset_choices():
    return [(v["label"], k) for k, v in _PRESETS.items()]


def latest_outputs(limit: int = 10):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(OUT_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p) for p in files[:limit] if p.is_file()]


def maybe_make_ogg(wav_path: Path) -> str:
    if not Path(FFMPEG).exists():
        return "ffmpeg not found; skipped .ogg export"
    ogg_path = wav_path.with_suffix(".ogg")
    subprocess.run(
        [FFMPEG, "-y", "-i", str(wav_path), "-c:a", "libopus", "-b:a", "48k", str(ogg_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return str(ogg_path)


def maybe_make_mp3(wav_path: Path) -> str:
    if not Path(FFMPEG).exists():
        return "ffmpeg not found; skipped .mp3 export"
    mp3_path = wav_path.with_suffix(".mp3")
    subprocess.run(
        [FFMPEG, "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return str(mp3_path)


def _atempo_chain(speed: float) -> str:
    if speed <= 0:
        raise ValueError("speed 必須大於 0")
    factors = []
    remaining = float(speed)
    while remaining < 0.5:
        factors.append(0.5)
        remaining /= 0.5
    while remaining > 2.0:
        factors.append(2.0)
        remaining /= 2.0
    factors.append(remaining)
    return ",".join(f"atempo={f:.6g}" for f in factors)


def maybe_adjust_speed(src_path: Path, speed: float) -> Path:
    speed = float(speed)
    if abs(speed - 1.0) < 1e-6:
        return src_path
    if not Path(FFMPEG).exists():
        raise RuntimeError("ffmpeg not found; cannot adjust speed")
    dst_path = src_path.with_name(f"{src_path.stem}-x{speed:.2f}{src_path.suffix}")
    subprocess.run(
        [FFMPEG, "-y", "-i", str(src_path), "-filter:a", _atempo_chain(speed), str(dst_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return dst_path


def to_simplified_chinese(text: str) -> str:
    return _cc_t2s.convert(text)


def build_prompt_text(text: str, preset: str, auto_t2s: bool, language: str) -> str:
    text = (text or "").strip()
    if not text:
        return text
    if auto_t2s and language == "Chinese":
        text = to_simplified_chinese(text)
    return text


def generate_tts_file(
    text: str,
    speaker: str = DEFAULT_SPEAKER,
    language: str = DEFAULT_LANGUAGE,
    max_new_tokens: Optional[int] = None,
    export_ogg: bool = True,
    export_mp3: bool = True,
    preset: str = DEFAULT_PRESET,
    auto_t2s: bool = True,
    speed: float = DEFAULT_SPEED,
    instruct: str = "",
):
    text = (text or "").strip()
    if not text:
        raise ValueError("請輸入要朗讀的文字。")

    preset_cfg = _PRESETS.get(preset, _PRESETS[DEFAULT_PRESET])
    if max_new_tokens is None:
        max_new_tokens = int(preset_cfg.get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS))

    final_text = build_prompt_text(text=text, preset=preset, auto_t2s=auto_t2s, language=language)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wav_path = OUT_DIR / f"{speaker}-{stamp}.wav"
    synthesize(
        text=final_text,
        out_path=str(wav_path),
        speaker=speaker,
        language=language,
        max_new_tokens=int(max_new_tokens),
    )

    wav_effective_path = maybe_adjust_speed(wav_path, speed)

    ogg_path = None
    ogg_result = "未輸出 .ogg"
    if export_ogg:
        try:
            ogg_result = maybe_make_ogg(wav_effective_path)
            ogg_path = ogg_result if ogg_result.endswith('.ogg') else None
        except Exception as e:
            ogg_result = f".ogg 轉檔失敗: {e}"

    mp3_path = None
    mp3_result = "未輸出 .mp3"
    if export_mp3:
        try:
            mp3_result = maybe_make_mp3(wav_effective_path)
            mp3_path = mp3_result if mp3_result.endswith('.mp3') else None
        except Exception as e:
            mp3_result = f".mp3 轉檔失敗: {e}"

    return {
        "wav_path": str(wav_effective_path),
        "ogg_path": ogg_path,
        "mp3_path": mp3_path,
        "info": f"WAV: {wav_effective_path}\nOGG: {ogg_result}\nMP3: {mp3_result}\nSPEED: {float(speed):.2f}x",
        "final_text": final_text,
        "preset": preset,
        "speaker": speaker,
        "language": language,
        "max_new_tokens": int(max_new_tokens),
        "auto_t2s": auto_t2s,
        "speed": float(speed),
        "instruct": (instruct or '').strip(),
    }
