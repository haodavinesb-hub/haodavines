# Tham khảo chi tiết

## Chọn model VieNeu nào

| Model | Chất lượng | Tốc độ | Sample rate | Gọi bằng |
|---|---|---|---|---|
| **v3 Turbo** *(mặc định)* | Tốt nhất trong bản mở | GPU RTF ≈0.02–0.5 · CPU int8 RTF 0.35 | 48 kHz | `Vieneu()` |
| **v3 Nano** *(preview)* | Thấp hơn rõ, nhất là tiếng Anh | CPU RTF 0.11–0.22 (~3× Turbo) | 24 kHz | `Vieneu(mode="v3nano")` |
| **v4** | Sát giọng gốc nhất | — | — | **Đóng, trả phí** — [vieneu.io](https://www.vieneu.io) |

Chỉ dùng Nano khi Turbo quá chậm trên máy bạn (laptop cũ, mini PC, board ARM, CPU
không có AVX-512/VNNI khiến bản int8 của Turbo bị méo).

## Dùng trực tiếp SDK Python

```python
from vieneu import Vieneu

tts = Vieneu()                       # GPU → PyTorch, không GPU → ONNX/CPU

# Giọng dựng sẵn
audio = tts.infer("Xin chào các bạn.", voice="Minh Quân")

# Clone tức thì
audio = tts.infer("Đây là giọng nhân bản.", ref_audio="mau.wav", denoise=True)

# Đăng ký giọng một lần rồi dùng theo tên — nhanh hơn khi đọc dài
tts.add_voice("Giọng của tôi", "mau.wav")
audio = tts.infer("Câu này dùng giọng đã lưu.", voice="Giọng của tôi")
tts.save_voices()                    # lưu lại để session sau vẫn còn

tts.save(audio, "out.wav")           # 48 kHz
```

Các hàm khác:

- `tts.list_preset_voices()` → list `(label, voice_id)` của 25 giọng dựng sẵn
- `tts.denoise("on.wav", out_path="sach.wav")` → khử ồn riêng, trả `(wav, sr)` 44.1 kHz
- `tts.infer_batch(texts, voice=...)` → chạy nhiều text trong **một** forward
  (lợi lớn trên GPU; trên CPU vẫn chạy nhưng tuần tự, không nhanh hơn)
- `tts.infer_stream(text, voice=...)` → stream từng frame, dùng cho real-time
- `tts.remove_voice(ten)`

Toàn bộ `denoise`, `add_voice` và voice cloning chạy được trên **mọi backend**,
kể cả bản CPU torch-free.

## 25 giọng dựng sẵn

- ⭐ **Nên bắt đầu với 10 giọng này** (tác giả chọn vì tự nhiên và ổn định):
  Adam bựa, Trúc Ly, Anh Khôi, Mai Anh, **Minh Quân** *(mặc định)*, Thùy Dung,
  Thiền Tâm Đức, Ngọc Huyền, Quang Sơn, Ngọc Trân
- **Bắc**: Minh Đức, Phạm Tuyên, Xuân Vĩnh, Thanh Bình, Ngọc Linh, Đoan Trang,
  Quỳnh Anh, Mạnh Dũng
- **Trung**: Quang Sơn, Ngọc Trân
- **Nam**: Adam, Thái Sơn, Thục Đoan, Minh Triết, Mỹ Duyên, Đức Trí, Kim Thanh

Xem danh sách thật từ máy bạn: `clone.py --list-voices`

## Fine-tune LoRA — tuỳ chọn nâng cao

Mặc định: LoRA rank 16 trên toàn bộ attention + MLP của backbone, lr 2e-4,
3 epoch, batch hiệu dụng 16, bf16.

| Tuỳ chọn | Ý nghĩa |
|---|---|
| `--epochs 3` / `--max-steps N` | Thời lượng train |
| `--r 16 --alpha 32` | Dung lượng LoRA. Giọng khó hoặc data nhiều → `--r 32` |
| `--target all` | Thêm LoRA cho acoustic decoder — **chất giọng bám sát hơn**, nhưng cần nhiều data hơn |
| `--no-ref` | Train chỉ dựa speaker embedding, không dùng clip tham chiếu (hợp khi một giọng, ít clip) |
| `--grad-checkpoint` | Tiết kiệm VRAM khi tăng `--batch-size` hoặc `--max-length` |
| `--merge` | Xuất luôn model đầy đủ đã merge |

Muốn bám giọng chặt nhất: **`--target all` + `--r 32`** với 20–30 phút data.

Lượng dữ liệu theo mục tiêu:

| Mục tiêu | Dữ liệu |
|---|---|
| Một giọng, bám chặt hơn clone | **10–30 phút** audio sạch (100–300 câu) |
| Nhiều giọng trong một model, hoặc đổi hẳn phong cách đọc | 2–4 giờ, chia đều |

Kết quả nằm trong `finetune/output/<ten>/`: `adapter/` (LoRA vài MB),
`checkpoint-*/`, `merged/` (model đầy đủ).

Đẩy lên Hugging Face:
```bash
uv run python finetune/merge_lora.py --adapter finetune/output/giong_toi/adapter \
    --out finetune/output/giong_toi/merged \
    --push-to-hub ten-cua-ban/VieNeu-TTS-v3-Turbo-giong-toi --private
```

## Fine-tune trên Google Colab (không có GPU)

Repo có sẵn [Colab notebook](https://colab.research.google.com/drive/1b9PO-lcGZX9pEkEwQmu8MfhSnjxKrALW).
GPU T4 miễn phí của Colab (16GB) thừa sức cho LoRA rank 16–32. Cách làm:

1. Upload thư mục dataset (`metadata.csv` + `raw_audio/`) lên Google Drive
2. Mount Drive trong notebook
3. Chạy đúng 3 lệnh trong phần "Fine-tuning (LoRA)" của README
4. Tải `finetune/output/<ten>/merged/` về máy

Nhớ tải model về trước khi Colab ngắt phiên — nếu không là mất hết.

## Chuẩn hoá text tiếng Việt

| Viết trong file | Nên đổi thành |
|---|---|
| `2025` | `hai nghìn không trăm hai mươi lăm` |
| `15/3/2024` | `ngày mười lăm tháng ba năm hai nghìn không trăm hai mươi tư` |
| `TP.HCM` | `Thành phố Hồ Chí Minh` |
| `150.000đ` | `một trăm năm mươi nghìn đồng` |
| `km/h` | `ki lô mét trên giờ` |
| `GDP` | `giê đê pê` |

v3 Turbo dùng phonemizer [sea-g2p](https://github.com/pnnbao97/sea-g2p) nên đọc
tiếng Việt khá chuẩn, nhưng số và viết tắt vẫn nên tự chuẩn hoá trước.

## Máy offline hoặc bị chặn Hugging Face

Model tải từ Hugging Face ở lần chạy đầu (`pnnbao-ump/VieNeu-TTS-v3-Turbo`).
Nếu máy không vào được HF (firewall công ty, proxy chặn, máy offline):

```bash
# Ở máy CÓ mạng
huggingface-cli download pnnbao-ump/VieNeu-TTS-v3-Turbo
huggingface-cli download OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano

# Copy ~/.cache/huggingface sang máy đích, rồi:
export HF_HUB_OFFLINE=1
```

Đổi chỗ lưu cache bằng `HF_HOME=/duong/dan/khac`.

## Nguồn

- [pnnbao97/VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) — Apache-2.0
- [VieNeu-TTS-v3-Turbo trên Hugging Face](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo)
- [sea-g2p](https://github.com/pnnbao97/sea-g2p) — phonemizer tiếng Việt của v3 Turbo
- API đã đối chiếu trực tiếp với package `vieneu` trên PyPI (`vieneu/v3turbo.py`,
  `vieneu/factory.py`), không chỉ dựa vào README
