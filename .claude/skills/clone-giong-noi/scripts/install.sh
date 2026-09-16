#!/usr/bin/env bash
# Cai dat VieNeu-TTS de clone giong noi tieng Viet chat luong cao.
# Dung:  bash install.sh
#        VIENEU_DIR=/path bash install.sh
set -euo pipefail

VIENEU_DIR="${VIENEU_DIR:-$HOME/VieNeu-TTS}"
REPO="https://github.com/pnnbao97/VieNeu-TTS.git"

echo "==> Thu muc cai dat: $VIENEU_DIR"

# --- uv: trinh quan ly moi truong ma repo khuyen dung ---
# uv sync tai dung ban ONNX Runtime da toi uu -> nhanh hon pip install nhieu.
if ! command -v uv >/dev/null 2>&1; then
    echo "==> Chua co uv, dang cai..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || { echo "LOI: cai uv that bai. Xem https://astral.sh/uv" >&2; exit 1; }
echo "==> uv $(uv --version 2>/dev/null || echo '?')"

# --- Clone hoac cap nhat ---
if [ -d "$VIENEU_DIR/.git" ]; then
    echo "==> Da co san, dang cap nhat..."
    git -C "$VIENEU_DIR" pull --ff-only
else
    echo "==> Dang tai ve tu GitHub..."
    git clone --depth 1 "$REPO" "$VIENEU_DIR"
fi

cd "$VIENEU_DIR"

# --- Chon bien cai dat theo phan cung ---
# GPU NVIDIA -> PyTorch (bat buoc neu muon fine-tune LoRA).
# Con lai   -> ONNX torch-free, nhanh hon tren CPU va ca Apple Silicon.
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "==> Phat hien GPU NVIDIA -> cai ban CUDA (PyTorch)"
    echo "    (can ban nay neu muon fine-tune LoRA de clone 'giong het')"
    uv sync --extra cuda
    BACKEND="GPU / PyTorch"
else
    echo "==> Khong co GPU NVIDIA -> cai ban ONNX torch-free"
    echo "    Tren macOS/Apple Silicon day cung la ban NHANH NHAT (nhanh hon MPS)."
    uv sync
    BACKEND="CPU / ONNX"
fi

cat <<MSG

==> Cai xong. Backend: $BACKEND

    Giao dien web:
        cd $VIENEU_DIR && uv run vieneu-web      # http://127.0.0.1:7860

    Clone giong tu dong lenh:
        bash $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/clone.py --help

MSG
if ! command -v nvidia-smi >/dev/null 2>&1; then
cat <<'MSG'
    LUU Y: khong co GPU NVIDIA nen KHONG fine-tune LoRA duoc (can ~6GB VRAM).
    Ban chi dung duoc clone tuc thi tu clip 3-8s. Muon "giong het" thi can
    fine-tune -> dung Google Colab (co GPU mien phi). Xem reference.md.
MSG
fi
