#!/usr/bin/env bash
# Cai dat ebook2audiobook de clone giong noi.
# Dung:  bash e2a-install.sh          -> cai vao ~/ebook2audiobook
#        E2A_DIR=/path bash e2a-install.sh
set -euo pipefail

E2A_DIR="${E2A_DIR:-$HOME/ebook2audiobook}"
REPO="https://github.com/DrewThomasson/ebook2audiobook.git"

echo "==> Thu muc cai dat: $E2A_DIR"

# --- Kiem tra Python: repo yeu cau >3.9 va <3.13 ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "LOI: khong tim thay python3. Cai Python 3.10-3.12 truoc." >&2
    exit 1
fi
PYV="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if ! python3 -c 'import sys; sys.exit(0 if (3,9) < sys.version_info[:2] < (3,13) else 1)'; then
    echo "LOI: Python $PYV khong duoc ho tro. Can >3.9 va <3.13." >&2
    exit 1
fi
echo "==> Python $PYV OK"

# --- Canh bao dung luong dia (model can ~10GB) ---
AVAIL_GB="$(df -Pk "$(dirname "$E2A_DIR")" | awk 'NR==2 {print int($4/1024/1024)}')"
if [ "${AVAIL_GB:-0}" -lt 10 ]; then
    echo "CANH BAO: chi con ${AVAIL_GB}GB trong. Model TTS can khoang 10GB." >&2
fi

# --- Clone hoac cap nhat ---
if [ -d "$E2A_DIR/.git" ]; then
    echo "==> Da co san, dang cap nhat..."
    git -C "$E2A_DIR" pull --ff-only
else
    echo "==> Dang tai ve tu GitHub..."
    git clone --depth 1 "$REPO" "$E2A_DIR"
fi

chmod +x "$E2A_DIR"/*.sh "$E2A_DIR"/*.command 2>/dev/null || true
echo "==> Phien ban: $(cat "$E2A_DIR/VERSION.txt" 2>/dev/null || echo 'khong ro')"

# --- Bao cao thiet bi ---
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "==> Phat hien GPU NVIDIA -> dung --device CUDA"
elif [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
    echo "==> Apple Silicon -> dung --device MPS"
else
    echo "==> Khong co GPU -> se chay CPU (CHAM)"
fi

cat <<'MSG'

==> Tai ve xong. Buoc cuoi: chay launcher chinh thuc mot lan de no tu cai
    Miniforge3 + cac goi he thong (ffmpeg, espeak-ng, sox, mediainfo,
    calibre, tesseract, nodejs, cmake) + moi truong Python.

    Lan chay dau MAT KHA LAU (tai vai GB).
MSG
echo "        cd $E2A_DIR && ./ebook2audiobook.sh --help"
echo
echo "    Sau do doc van ban:"
echo "        bash $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/e2a-doc.sh <file.txt> <giong-mau.wav>"
