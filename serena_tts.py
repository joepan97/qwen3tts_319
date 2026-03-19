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
DEFAULT_DEVICE = os.environ.get('QWEN_TTS_DEVICE', 'auto')
DEFAULT_DTYPE = os.environ.get('QWEN_TTS_DTYPE', 'auto')
DEFAULT_FLASH_ATTN = os.environ.get('QWEN_TTS_FLASH_ATTN', 'auto')

_MODEL = None


def resolve_device() -> str:
    if DEFAULT_DEVICE != 'auto':
        return DEFAULT_DEVICE
    if torch.cuda.is_available():
        return 'cuda:0'
    return 'cpu'


def resolve_dtype(device: str):
    if DEFAULT_DTYPE != 'auto':
        mapping = {
            'float32': torch.float32,
            'fp32': torch.float32,
            'float16': torch.float16,
            'fp16': torch.float16,
            'bfloat16': torch.bfloat16,
            'bf16': torch.bfloat16,
        }
        if DEFAULT_DTYPE.lower() not in mapping:
            raise ValueError(f'Unsupported QWEN_TTS_DTYPE: {DEFAULT_DTYPE}')
        return mapping[DEFAULT_DTYPE.lower()]
    if str(device).startswith('cuda'):
        return torch.float16
    return torch.float32


def resolve_attn_impl(device: str):
    if DEFAULT_FLASH_ATTN == 'off':
        return None
    if DEFAULT_FLASH_ATTN == 'on':
        return 'flash_attention_2'
    if str(device).startswith('cuda'):
        return 'flash_attention_2'
    return None


def get_model():
    global _MODEL
    if _MODEL is None:
        t0 = time.time()
        device = resolve_device()
        dtype = resolve_dtype(device)
        attn_impl = resolve_attn_impl(device)
        kwargs = {
            'device_map': device,
            'dtype': dtype,
        }
        if attn_impl:
            kwargs['attn_implementation'] = attn_impl
        _MODEL = Qwen3TTSModel.from_pretrained(MODEL_ID, **kwargs)
        print(
            f'[serena-tts] model loaded in {time.time()-t0:.2f}s '
            f'(device={device}, dtype={dtype}, attn={attn_impl or "default"})',
            file=sys.stderr,
        )
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
