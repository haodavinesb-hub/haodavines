#!/usr/bin/env bash
# Fine-tune LoRA de clone giong "giong het" - can GPU NVIDIA ~6GB VRAM.
# Dung:  bash finetune.sh <ten_giong> <thu_muc_dataset> [clip_tham_chieu.wav]
#
# Thu muc dataset phai co dang:
#   dataset/
#     metadata.csv     moi dong:  ten_file.wav|noi dung cau doc
#     raw_audio/       cac file audio duoc nhac trong metadata.csv
#
# Yeu cau du lieu: 10-30 phut audio SACH cua MOT nguoi (100-300 cau khac nhau).
# Moi clip 1-20 giay, khong nhac nen, it vang, text khop dung tung dau cau.
set -euo pipefail

VIENEU_DIR="${VIENEU_DIR:-$HOME/VieNeu-TTS}"
TEN_GIONG="${1:-}"
DATASET_SRC="${2:-}"
REF_WAV="${3:-}"

if [ -z "$TEN_GIONG" ] || [ -z "$DATASET_SRC" ]; then
    echo "Dung: bash finetune.sh <ten_giong> <thu_muc_dataset> [clip_tham_chieu.wav]" >&2
    echo "VD:   bash finetune.sh giong_toi ./du-lieu-giong ./mau.wav" >&2
    exit 1
fi

# Ten giong dung lam ten thu muc va ten run -> chi cho chu thuong, so, gach duoi
if ! echo "$TEN_GIONG" | grep -qE '^[a-z0-9_]+$'; then
    echo "LOI: ten_giong chi duoc gom chu thuong, so va dau gach duoi (a-z 0-9 _)." >&2
    exit 1
fi

[ -d "$VIENEU_DIR" ] || { echo "LOI: chua cai VieNeu-TTS tai $VIENEU_DIR. Chay install.sh truoc." >&2; exit 1; }
[ -d "$DATASET_SRC" ] || { echo "LOI: khong thay thu muc dataset: $DATASET_SRC" >&2; exit 1; }
[ -f "$DATASET_SRC/metadata.csv" ] || { echo "LOI: thieu $DATASET_SRC/metadata.csv" >&2; exit 1; }
[ -d "$DATASET_SRC/raw_audio" ] || { echo "LOI: thieu $DATASET_SRC/raw_audio/" >&2; exit 1; }

if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "LOI: khong thay GPU NVIDIA. Train LoRA can CUDA (~6GB VRAM)." >&2
    echo "     Khong co GPU -> dung Google Colab. Xem reference.md." >&2
    exit 1
fi

DATASET_SRC="$(cd "$DATASET_SRC" && pwd)"
SO_CLIP="$(tail -n +1 "$DATASET_SRC/metadata.csv" | grep -c . || true)"
echo "==> Giong:   $TEN_GIONG"
echo "==> Dataset: $DATASET_SRC  ($SO_CLIP dong metadata)"
if [ "$SO_CLIP" -lt 100 ]; then
    echo "    CANH BAO: khuyen nghi 100-300 cau. It hon de bi overfit." >&2
fi

cd "$VIENEU_DIR"
DATASET_DIR="finetune/dataset_$TEN_GIONG"

echo
echo "==> [1/4] Cai phu thuoc cho fine-tune (torch, transformers, peft, accelerate)"
uv sync --extra finetune

echo
echo "==> [2/4] Chuan bi du lieu (chay CPU: phien am sea-g2p + ma hoa codec MOSS)"
rm -rf "$DATASET_DIR"
mkdir -p "$DATASET_DIR"
cp -r "$DATASET_SRC/metadata.csv" "$DATASET_SRC/raw_audio" "$DATASET_DIR/"
uv run python finetune/prepare_dataset.py --dataset-dir "$DATASET_DIR" --speaker "$TEN_GIONG"

echo
echo "==> [3/4] Train LoRA (theo doi 'acc_cb0' trong log: phai 0.2-0.4 tu dau va TANG dan;"
echo "          neu gan 0 thi du lieu sai - text khong khop audio)"
uv run python finetune/train_lora.py \
    --data "$DATASET_DIR/train.parquet" \
    --run "$TEN_GIONG" \
    --merge

MERGED="finetune/output/$TEN_GIONG/merged"

if [ -n "$REF_WAV" ] && [ -f "$REF_WAV" ]; then
    echo
    echo "==> [4/4] Dong goi giong san vao model (khoi can clip mau khi dung)"
    uv run python finetune/make_voice.py \
        --audio "$(cd "$(dirname "$REF_WAV")" && pwd)/$(basename "$REF_WAV")" \
        --name "$TEN_GIONG" \
        --out "$MERGED"
else
    echo
    echo "==> [4/4] Bo qua dong goi giong (khong truyen clip_tham_chieu.wav)"
fi

cat <<MSG

==> XONG. Model nam tai: $VIENEU_DIR/$MERGED

    Dung model vua train:
        cd $VIENEU_DIR
        uv run python <duong-dan>/clone.py \\
            --text bai-viet.txt --ref mau.wav \\
            --backbone $MERGED -o ket-qua.wav

    LUU Y: model da fine-tune chi chay tren GPU (PyTorch).
    Duong CPU/ONNX dung do thi export san cua model goc nen KHONG nhan model nay.
MSG
