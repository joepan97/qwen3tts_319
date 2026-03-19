#!/bin/sh
set -eu

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found" >&2
  exit 1
fi

sudo apt update
sudo apt install -y python3 python3-venv ffmpeg sox

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -U pip setuptools wheel

cat <<'EOF'
============================================================
注意：NVIDIA / CUDA 版 PyTorch 請依你的驅動與 CUDA 版本，
到 PyTorch 官方網站選對應安裝指令後再執行。

例如（僅示意，請依官方指令替換）：
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124

安裝完 torch / torchaudio 後，再執行：
  pip install -r requirements.txt
============================================================
EOF

pip install -r requirements.txt

echo "完成。若要使用 NVIDIA，請確認 torch.cuda.is_available() 為 True。"
