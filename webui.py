#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

import gradio as gr

from tts_service import (
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_PRESET,
    DEFAULT_SPEAKER,
    DEFAULT_SPEED,
    LANGUAGES,
    SPEAKERS,
    generate_tts_file,
    latest_outputs,
    preset_choices,
)

DEFAULT_HOST = os.environ.get("QWEN_TTS_WEBUI_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("QWEN_TTS_WEBUI_PORT", "7860"))
DEFAULT_SHARE = os.environ.get("QWEN_TTS_WEBUI_SHARE", "0") == "1"
PRESET_MAP = dict(preset_choices())
PRESET_LABELS = list(PRESET_MAP.keys())
DEFAULT_PRESET_LABEL = next((label for label, value in PRESET_MAP.items() if value == DEFAULT_PRESET), PRESET_LABELS[0])
TONE_PRESETS = {
    "自訂": "",
    "自然": "請用自然、日常、平穩的口氣來讀。",
    "溫柔": "請用溫柔、平靜、柔和的口氣來讀。",
    "生氣": "請用生氣、不耐煩、帶有情緒的口氣來讀。",
    "難過": "請用難過、低落、有點委屈的口氣來讀。",
    "開朗": "請用開朗、有精神、輕快的口氣來讀。",
    "嚴肅": "請用嚴肅、認真、直接的口氣來讀。",
    "播報": "請用像新聞播報一樣清楚、穩定的口氣來讀。",
    "故事": "請用像說故事一樣有畫面感、帶節奏的口氣來讀。",
}


def format_error_message(exc: Exception) -> str:
    msg = str(exc).strip() or exc.__class__.__name__
    raw = f"{exc.__class__.__name__}: {msg}"
    low = raw.lower()

    if "請輸入要朗讀的文字" in raw or "no text provided" in low:
        return "生成失敗：你還沒有輸入要朗讀的文字。"
    if "unsupported speakers" in low:
        return f"生成失敗：目前選到的 speaker 不支援。\n\n詳細：{raw}"
    if "unsupported languages" in low:
        return f"生成失敗：目前選到的語言不支援。\n\n詳細：{raw}"
    if "ffmpeg not found" in low:
        return f"生成失敗：找不到 ffmpeg，所以無法做音檔轉檔或語速調整。\n\n詳細：{raw}"
    if "invalidpatherror" in low or "allowed_paths" in low or "dotfiles located" in low:
        return f"生成失敗：WebUI 被安全限制擋住，無法把產生的音檔回傳到頁面。\n\n詳細：{raw}"
    if "unexpected keyword argument 'instruct'" in low:
        return f"生成失敗：目前執行中的 WebUI / TTS 服務版本不一致，請重整頁面後再試一次；如果還不行，重啟 WebUI。\n\n詳細：{raw}"
    if "takes" in low and "positional arguments but" in low and "were given" in low:
        return f"生成失敗：前端送出的欄位數量和後端函式不一致，通常代表 WebUI 還在跑舊版程式。\n\n詳細：{raw}"

    return f"生成失敗：{msg}\n\n詳細：{raw}"


def preset_to_values(preset_label: str):
    preset = PRESET_MAP.get(preset_label, DEFAULT_PRESET)
    if preset == "gentle":
        return 832, True, 0.92
    if preset == "story":
        return 896, True, 0.95
    if preset == "slow_clear":
        return 960, True, 0.82
    if preset == "lively":
        return 800, True, 1.08
    return DEFAULT_MAX_NEW_TOKENS, True, DEFAULT_SPEED


def tone_preset_to_text(tone_preset: str):
    return TONE_PRESETS.get(tone_preset, "")


def generate_tts(
    text: str,
    speaker: str,
    language: str,
    preset_label: str,
    tone_instruction: str,
    max_new_tokens: int,
    speed: float,
    export_ogg: bool,
    export_mp3: bool,
    auto_t2s: bool,
):
    try:
        result = generate_tts_file(
            text=text,
            speaker=speaker,
            language=language,
            max_new_tokens=int(max_new_tokens),
            export_ogg=export_ogg,
            export_mp3=export_mp3,
            preset=PRESET_MAP.get(preset_label, DEFAULT_PRESET),
            auto_t2s=auto_t2s,
            speed=float(speed),
            instruct=tone_instruction,
        )
        latest = latest_outputs(limit=20)
        download_value = result["mp3_path"] or result["ogg_path"] or result["wav_path"]
        out_dir = str(Path(__file__).resolve().parent / "out")
        return (
            result["wav_path"],
            result["info"],
            result["final_text"],
            result["wav_path"],
            out_dir,
            latest,
            download_value,
        )
    except Exception as e:
        raise gr.Error(format_error_message(e))


def refresh_latest():
    latest = latest_outputs(limit=20)
    default = latest[0] if latest else None
    return latest, default


def open_output_folder():
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["open", str(out_dir)], check=True)
    return str(out_dir)


def reveal_latest_file():
    latest = latest_outputs(limit=1)
    if not latest:
        raise gr.Error("目前還沒有生成檔案。")
    latest_path = latest[0]
    open_path(latest_path, reveal=True)
    return latest_path


with gr.Blocks(title="Qwen3-TTS Local WebUI") as demo:
    gr.Markdown(
        "# Qwen3-TTS 本機 WebUI\n"
        "支援語調預設、口氣選項、口氣說明（中文）、繁中轉簡中、最新輸出清單，以及本機 API。\n\n"
        "註：語調預設只會影響語速與生成參數；如果你想指定情緒/口氣，可以先選「口氣選項」，再視需要微調下面的中文說明。"
    )

    with gr.Row():
        with gr.Column(scale=3):
            text = gr.Textbox(label="文字", lines=8, placeholder="輸入想要朗讀的內容…")
            with gr.Row():
                speaker = gr.Dropdown(
                    choices=SPEAKERS,
                    value=DEFAULT_SPEAKER if DEFAULT_SPEAKER in SPEAKERS else SPEAKERS[0],
                    label="Speaker",
                )
                language = gr.Dropdown(choices=LANGUAGES, value=DEFAULT_LANGUAGE, label="Language")
            with gr.Row():
                preset = gr.Dropdown(choices=PRESET_LABELS, value=DEFAULT_PRESET_LABEL, label="語調 / 風格預設")
                max_new_tokens = gr.Slider(
                    minimum=128,
                    maximum=2048,
                    step=64,
                    value=DEFAULT_MAX_NEW_TOKENS,
                    label="Max new tokens",
                )
            tone_preset = gr.Dropdown(choices=list(TONE_PRESETS.keys()), value="自訂", label="口氣選項")
            tone_instruction = gr.Textbox(
                label="口氣說明（中文）",
                lines=2,
                placeholder="例如：請用溫柔、平靜、像睡前說故事的口氣來讀。",
            )
            speed = gr.Slider(minimum=0.5, maximum=1.5, step=0.05, value=DEFAULT_SPEED, label="語速")
            with gr.Row():
                export_ogg = gr.Checkbox(value=True, label="同時輸出 .ogg / Opus")
                export_mp3 = gr.Checkbox(value=True, label="同時輸出 .mp3")
                auto_t2s = gr.Checkbox(value=True, label="繁中自動轉簡中（中文時）")
            submit = gr.Button("生成語音", variant="primary")
        with gr.Column(scale=2):
            audio = gr.Audio(label="預覽", type="filepath")
            info = gr.Textbox(label="輸出資訊 / 錯誤訊息", lines=6)
            final_text = gr.Textbox(label="實際送進模型的文字", lines=6)
            latest_path_box = gr.Textbox(label="最新檔案路徑（可直接複製）", lines=2)
            folder_path_box = gr.Textbox(
                label="輸出資料夾路徑（可直接複製）",
                value=str((Path(__file__).resolve().parent / "out")),
                lines=2,
            )

    gr.Markdown("## 最新輸出")
    with gr.Row():
        latest_files = gr.File(label="最近生成的檔案", value=latest_outputs(limit=20), file_count="multiple")
        latest_download = gr.File(label="最新檔 / 可直接下載")
    with gr.Row():
        refresh = gr.Button("重新整理最新輸出")
        open_folder_btn = gr.Button("打開輸出資料夾")
        reveal_latest_btn = gr.Button("Finder 選取最新檔")

    preset.change(fn=preset_to_values, inputs=[preset], outputs=[max_new_tokens, auto_t2s, speed])
    tone_preset.change(fn=tone_preset_to_text, inputs=[tone_preset], outputs=[tone_instruction])
    submit.click(
        fn=generate_tts,
        inputs=[text, speaker, language, preset, tone_instruction, max_new_tokens, speed, export_ogg, export_mp3, auto_t2s],
        outputs=[audio, info, final_text, latest_path_box, folder_path_box, latest_files, latest_download],
    )
    refresh.click(fn=refresh_latest, outputs=[latest_files, latest_download])
    open_folder_btn.click(fn=open_output_folder, outputs=[folder_path_box])
    reveal_latest_btn.click(fn=reveal_latest_file, outputs=[latest_path_box])


if __name__ == "__main__":
    demo.launch(
        server_name=DEFAULT_HOST,
        server_port=DEFAULT_PORT,
        share=DEFAULT_SHARE,
        inbrowser=False,
        allowed_paths=[str((Path(__file__).resolve().parent / "out").resolve())],
    )
