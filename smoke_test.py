import os, time, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

MODEL_ID = os.environ.get('QWEN_TTS_MODEL', 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice')
OUT = os.environ.get('QWEN_TTS_OUT', 'smoke-test.wav')
TEXT = os.environ.get('QWEN_TTS_TEXT', '你好，我是 Zee。這是一段在 Mac mini 上測試的語音。')

print('loading', MODEL_ID, flush=True)
t0 = time.time()
model = Qwen3TTSModel.from_pretrained(
    MODEL_ID,
    device_map='cpu',
    dtype=torch.float32,
)
print('loaded_in_sec', round(time.time()-t0, 2), flush=True)
langs = model.get_supported_languages()
print('languages', langs[:20] if langs else None, flush=True)
spks = model.get_supported_speakers()
print('speaker_count', len(spks) if spks else None, flush=True)
print('speakers_head', spks[:10] if spks else None, flush=True)
speaker = None
for cand in ['Cherry', 'Ethan', 'Chelsie', 'Serena', 'Dylan', 'anna']:
    if spks and cand.lower() in [s.lower() for s in spks]:
        speaker = cand
        break
if speaker is None and spks:
    speaker = spks[0]
print('using_speaker', speaker, flush=True)

t1 = time.time()
wavs, sr = model.generate_custom_voice(
    text=TEXT,
    speaker=speaker,
    language='Chinese',
    non_streaming_mode=True,
    max_new_tokens=600,
)
print('synth_sec', round(time.time()-t1, 2), flush=True)
sf.write(OUT, wavs[0], sr)
print('saved', OUT, sr, len(wavs[0]), flush=True)
