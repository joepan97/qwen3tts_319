#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

MODEL_ID = os.environ.get('QWEN_TTS_MODEL', 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice')
DEFAULT_SPEAKER = os.environ.get('QWEN_TTS_SPEAKER', 'serena')
DEFAULT_LANGUAGE = os.environ.get('QWEN_TTS_LANGUAGE', 'Chinese')
DEFAULT_MAX_NEW_TOKENS = int(os.environ.get('QWEN_TTS_MAX_NEW_TOKENS', '700'))

_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        t0 = time.time()
        _MODEL = Qwen3TTSModel.from_pretrained(
            MODEL_ID,
            device_map='cpu',
            dtype=torch.float32,
        )
        print(f'[serena-tts] model loaded in {time.time()-t0:.2f}s', file=sys.stderr)
    return _MODEL


def synthesize(text: str, out_path: str, speaker: str, language: str, max_new_tokens: int, instruct: str | None = None):
    model = get_model()
    t1 = time.time()
    kwargs = {
        'text': text,
        'speaker': speaker,
        'language': language,
        'non_streaming_mode': True,
        'max_new_tokens': max_new_tokens,
    }
    if instruct:
        kwargs['instruct'] = instruct
    wavs, sr = model.generate_custom_voice(**kwargs)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_path, wavs[0], sr)
    print(f'[serena-tts] synthesized in {time.time()-t1:.2f}s -> {out_path}', file=sys.stderr)
    return out_path, sr, len(wavs[0])


def main():
    parser = argparse.ArgumentParser(description='Generate speech with Qwen3-TTS using Serena by default.')
    parser.add_argument('text', nargs='*', help='Text to speak. If omitted, reads from stdin.')
    parser.add_argument('-o', '--out', default='out/serena.wav', help='Output wav path')
    parser.add_argument('--speaker', default=DEFAULT_SPEAKER, help='Speaker id (default: serena)')
    parser.add_argument('--language', default=DEFAULT_LANGUAGE, help='Language label (default: Chinese)')
    parser.add_argument('--max-new-tokens', type=int, default=DEFAULT_MAX_NEW_TOKENS)
    args = parser.parse_args()

    text = ' '.join(args.text).strip()
    if not text:
        text = sys.stdin.read().strip()
    if not text:
        parser.error('No text provided.')

    synthesize(text=text, out_path=args.out, speaker=args.speaker, language=args.language, max_new_tokens=args.max_new_tokens)


if __name__ == '__main__':
    main()
