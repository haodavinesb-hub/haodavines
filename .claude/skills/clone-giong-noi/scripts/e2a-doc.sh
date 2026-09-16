#!/usr/bin/env bash
# Doc van ban bang giong clone.
# Dung:  bash e2a-doc.sh <file_nguon> <file_giong_mau> [ma_ngon_ngu] [dinh_dang]
# VD:    bash e2a-doc.sh bai-viet.txt giong-cua-toi.wav
#        bash e2a-doc.sh sach.epub giong.wav eng m4b
set -euo pipefail

E2A_DIR="${E2A_DIR:-$HOME/ebook2audiobook}"
EBOOK="${1:-}"
VOICE="${2:-}"
LANG_CODE="${3:-vie}"
OUT_FORMAT="${4:-mp3}"

if [ -z "$EBOOK" ] || [ -z "$VOICE" ]; then
    echo "Dung: bash e2a-doc.sh <file_nguon> <file_giong_mau> [ma_ngon_ngu] [dinh_dang]" >&2
    echo "VD:   bash e2a-doc.sh bai-viet.txt giong-cua-toi.wav" >&2
    exit 1
fi

if [ ! -d "$E2A_DIR" ]; then
    echo "LOI: chua cai ebook2audiobook tai $E2A_DIR" >&2
    echo "Chay truoc: bash $(dirname "${BASH_SOURCE[0]}")/e2a-install.sh" >&2
    exit 1
fi
[ -f "$EBOOK" ] || { echo "LOI: khong thay file nguon: $EBOOK" >&2; exit 1; }
[ -f "$VOICE" ] || { echo "LOI: khong thay file giong mau: $VOICE" >&2; exit 1; }

# Duong dan tuyet doi vi ta se cd sang thu muc khac
EBOOK="$(cd "$(dirname "$EBOOK")" && pwd)/$(basename "$EBOOK")"
VOICE="$(cd "$(dirname "$VOICE")" && pwd)/$(basename "$VOICE")"

# --- Chon TTS engine theo ngon ngu ---
# XTTS chi ho tro 17 thu tieng, KHONG co tieng Viet (xem lib/conf_models.py).
# Voi tieng Viet phai dung FAIRSEQ (Meta MMS) + buoc voice conversion.
XTTS_LANGS="ara ces deu eng fra hin hun ita jpn kor nld pol por rus spa tur zho"
if echo "$XTTS_LANGS" | grep -qw "$LANG_CODE"; then
    ENGINE="xtts"
else
    ENGINE="fairseq"
    echo "==> '$LANG_CODE' khong co trong XTTS -> dung FAIRSEQ + voice conversion."
    echo "    Giong clone se KEM giong mau hon so voi tieng Anh."
fi

# --- Chon thiet bi ---
if command -v nvidia-smi >/dev/null 2>&1; then
    DEVICE="CUDA"
elif [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
    DEVICE="MPS"
else
    DEVICE="CPU"
    echo "==> Khong co GPU -> chay CPU, se CHAM."
fi

echo "==> Nguon:     $EBOOK"
echo "==> Giong mau: $VOICE"
echo "==> Ngon ngu:  $LANG_CODE | Engine: $ENGINE | Thiet bi: $DEVICE"
echo

cd "$E2A_DIR"
./ebook2audiobook.sh --headless \
    --ebook "$EBOOK" \
    --voice "$VOICE" \
    --language "$LANG_CODE" \
    --tts_engine "$ENGINE" \
    --device "$DEVICE" \
    --output_format "$OUT_FORMAT"

echo
echo "==> Xong. Ket qua trong: $E2A_DIR/audiobooks/"
