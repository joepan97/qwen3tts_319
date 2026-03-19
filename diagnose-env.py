#!/usr/bin/env python3
import json
import os
import platform
import shutil

import torch

result = {
    "platform": platform.platform(),
    "python": platform.python_version(),
    "ffmpeg": shutil.which("ffmpeg"),
    "sox": shutil.which("sox"),
    "QWEN_TTS_DEVICE": os.environ.get("QWEN_TTS_DEVICE"),
    "QWEN_TTS_DTYPE": os.environ.get("QWEN_TTS_DTYPE"),
    "QWEN_TTS_FLASH_ATTN": os.environ.get("QWEN_TTS_FLASH_ATTN"),
    "torch_version": getattr(torch, "__version__", None),
    "cuda_available": torch.cuda.is_available(),
    "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
}

if torch.cuda.is_available():
    devices = []
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        devices.append({
            "index": i,
            "name": props.name,
            "total_memory_gb": round(props.total_memory / (1024**3), 2),
        })
    result["cuda_devices"] = devices

print(json.dumps(result, ensure_ascii=False, indent=2))
