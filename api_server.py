#!/usr/bin/env python3
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from tts_service import generate_tts_file, latest_outputs, preset_choices, SPEAKERS, LANGUAGES

HOST = os.environ.get("QWEN_TTS_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("QWEN_TTS_API_PORT", "7861"))

app = FastAPI(title="Qwen3-TTS Local API")


class SynthesizeRequest(BaseModel):
    text: str
    speaker: str = "serena"
    language: str = "Chinese"
    max_new_tokens: int | None = None
    export_ogg: bool = True
    export_mp3: bool = True
    preset: str = "balanced"
    auto_t2s: bool = True
    speed: float = 1.0


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/meta")
def meta():
    return {
        "speakers": SPEAKERS,
        "languages": LANGUAGES,
        "presets": [{"label": label, "value": value} for label, value in preset_choices()],
    }


@app.get("/latest")
def latest(limit: int = 10):
    return {"files": latest_outputs(limit=limit)}


@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    try:
        return generate_tts_file(
            text=req.text,
            speaker=req.speaker,
            language=req.language,
            max_new_tokens=req.max_new_tokens,
            export_ogg=req.export_ogg,
            export_mp3=req.export_mp3,
            preset=req.preset,
            auto_t2s=req.auto_t2s,
            speed=req.speed,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
