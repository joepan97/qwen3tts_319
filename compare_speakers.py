import os, time, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

MODEL_ID='Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice'
TEXT='Joe，這是 Zee 的語音測試。今天天氣不錯，晚點如果需要，我也可以直接用語音回覆你。'
SPEAKERS=['serena','vivian','ono_anna']
OUTDIR='speaker-tests'
os.makedirs(OUTDIR, exist_ok=True)

print('loading', MODEL_ID, flush=True)
model=Qwen3TTSModel.from_pretrained(MODEL_ID, device_map='cpu', dtype=torch.float32)
print('loaded', flush=True)
for spk in SPEAKERS:
    t=time.time()
    wavs, sr = model.generate_custom_voice(text=TEXT, speaker=spk, language='Chinese', non_streaming_mode=True, max_new_tokens=700)
    path=os.path.join(OUTDIR, f'{spk}.wav')
    sf.write(path, wavs[0], sr)
    print(spk, path, sr, len(wavs[0]), round(time.time()-t,2), flush=True)
