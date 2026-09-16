---
name: clone-giong-noi
description: Clone giọng nói và đọc văn bản dài (audiobook, voiceover) bằng ebook2audiobook, hỗ trợ tiếng Việt. Dùng khi người dùng muốn giả giọng, nhân bản giọng nói, đọc sách nói, lồng tiếng, chuyển text/ebook (.epub .pdf .txt .docx) thành file audio, hoặc nhắc tới ebook2audiobook, XTTS, voice cloning, TTS tiếng Việt.
---

# Clone giọng nói & đọc văn bản dài (ebook2audiobook)

Bọc công cụ [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook)
(Apache-2.0, ~20k sao) để clone giọng từ một file mẫu rồi đọc văn bản dài
thành audiobook.

## ⚠️ ĐỌC TRƯỚC: giới hạn với tiếng Việt

Đây là điều README không nói rõ, đã kiểm chứng trong `lib/conf_models.py`:

**XTTSv2 KHÔNG hỗ trợ tiếng Việt.** Danh sách ngôn ngữ của XTTS chỉ có 17 thứ
tiếng (`ara ces deu eng fra hin hun ita jpn kor nld pol por rus spa tur zho`) —
không có `vie`.

Với `--language vie`, ebook2audiobook chạy đường khác:

1. **FAIRSEQ (Meta MMS)** sinh tiếng Việt bằng **giọng nội bộ cố định**
   (`"voice": None, "voices": {}`) — tự nó KHÔNG clone được giọng.
2. Nếu có `--voice`, hệ thống bật cờ `use_zs` và chạy thêm bước
   **voice conversion** (mặc định `knnvc`) để ép giọng nội bộ đó sang giống
   giọng mẫu của bạn.

**Hệ quả thực tế:** clone giọng tiếng Việt ở đây là *chuyển đổi giọng sau khi
tổng hợp*, không phải clone gốc. Độ giống và độ tự nhiên **thấp hơn rõ rệt** so
với tiếng Anh, ngữ điệu sẽ hơi phẳng vì đến từ model MMS 16kHz.

**Nếu ưu tiên chất lượng tiếng Việt → dùng [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS)**
(native tiếng Việt, clone từ clip 3–8s, chạy CPU real-time). Xem `reference.md`.
Dùng ebook2audiobook khi bạn cần **pipeline sách nói hoàn chỉnh** (đọc thẳng
`.epub`/`.pdf`, tự tách chương, xuất `.m4b`) hoặc cần **đa ngôn ngữ**.

## Cài đặt

```bash
bash .claude/skills/clone-giong-noi/scripts/install.sh
```

Mặc định cài vào `~/ebook2audiobook`. Đổi chỗ khác:
`E2A_DIR=/duong/dan/khac bash .../install.sh`

Script sẽ clone repo rồi gọi launcher chính thức `ebook2audiobook.sh`, launcher
này tự cài Miniforge3 + các gói hệ thống (ffmpeg, espeak-ng, sox, mediainfo,
calibre, tesseract, nodejs, cmake) và môi trường Python.

**Yêu cầu:** Python >3.9 và <3.13 · tối thiểu 2GB RAM / 1GB VRAM ·
khuyến nghị 8GB RAM / 4GB VRAM · cần ~10GB đĩa trống cho model.
Chạy CPU được nhưng **rất chậm** — 1–2 phút audio có thể mất vài phút.

## Dùng nhanh

```bash
bash .claude/skills/clone-giong-noi/scripts/doc.sh <file_text_hoac_ebook> <file_giong_mau.wav>
```

Ví dụ:
```bash
bash .claude/skills/clone-giong-noi/scripts/doc.sh bai-viet.txt giong-cua-toi.wav
```

Kết quả nằm trong `~/ebook2audiobook/audiobooks/`.

## Gọi trực tiếp (headless)

```bash
cd ~/ebook2audiobook
./ebook2audiobook.sh --headless \
  --ebook bai-viet.txt \
  --voice giong-mau.wav \
  --language vie \
  --tts_engine fairseq \
  --device CPU \
  --output_format mp3
```

Mở giao diện web thay vì CLI: bỏ `--headless`, rồi vào `http://localhost:7860/`.

## Tham số hay dùng

| Tham số | Ý nghĩa |
|---|---|
| `--ebook` | File nguồn: `.txt .epub .pdf .docx .mobi .html .rtf .odt`… |
| `--voice` | File giọng mẫu để clone (**bắt buộc nếu muốn clone**) |
| `--language` | Mã ISO-639-3: `vie` (tiếng Việt), `eng`, `jpn`… Mã 2 chữ cũng được |
| `--tts_engine` | `xtts` `bark` `vits` `fairseq` `tacotron` `yourtts`. Tiếng Việt → `fairseq` |
| `--device` | `CPU` `CUDA` `MPS` `ROCM` `XPU` `JETSON` |
| `--output_format` | `mp3` `m4b` `wav` `flac` `aac` `ogg` `m4a` `mp4` |
| `--speed` | Tốc độ đọc, mặc định `1.0` |
| `--temperature` | Độ biến thiên giọng, mặc định `0.75`. Giảm → đều hơn |
| `--repetition_penalty` | Mặc định `2.0`. Tăng nếu bị lặp từ khi đọc dài |
| `--output_dir` | Thư mục xuất |

Xem đủ tham số: `./ebook2audiobook.sh --help`

## File giọng mẫu

- **Độ dài lý tưởng: 1–5 phút** (theo README). Ít hơn 30s là giọng ra sẽ kém.
- Không cần thu studio — E2A tự khử ồn và tách nhạc nền.
- Định dạng nào cũng được, nhưng `.wav` 1 kênh là an toàn nhất.

## Điều khiển ngắt nghỉ trong text (SML tags)

Chèn thẳng vào file text:

- `[break]` — nghỉ ngắn 0.3–0.6s
- `[pause]` — nghỉ 1.0–1.6s
- `[pause:3]` — nghỉ đúng 3 giây
- `[voice:/duong/dan/giong2.wav]...[/voice]` — đổi sang giọng khác cho đoạn này

Rất hữu ích cho đoạn 1–2 phút: chèn `[pause]` giữa các đoạn văn để nghe đỡ bị dồn.

## Khắc phục sự cố

| Triệu chứng | Xử lý |
|---|---|
| Giọng tiếng Việt nghe không giống mẫu | Bản chất của đường FAIRSEQ + voice conversion. Thử đổi model VC — xem `reference.md`. Hoặc chuyển sang VieNeu-TTS |
| Đọc sai số / ngày tháng / viết tắt | Chuẩn hoá text **trước** khi đưa vào: viết "hai nghìn không trăm hai lăm" thay vì "2025", "Thành phố Hồ Chí Minh" thay vì "TP.HCM" |
| Lặp từ, trôi giọng khi đọc dài | Tăng `--repetition_penalty`, giảm `--temperature`, hoặc cắt text thành file nhỏ hơn |
| Quá chậm | Đây là CPU. Dùng `--device CUDA` nếu có GPU NVIDIA, hoặc đổi `--tts_engine` sang loại nhẹ (`vits`, `tacotron`) — nhưng các engine này không có tiếng Việt |
| Lỗi Python version | Cần >3.9 và <3.13. Python 3.13+ sẽ fail |
| Chạy lại sau khi tắt, web UI trắng | Refresh lại trang gradio để nối socket mới |

## Lưu ý pháp lý

Chỉ clone giọng khi **có sự đồng ý của chủ giọng**. Dùng giọng người thật không
xin phép có thể vi phạm quyền nhân thân về hình ảnh/giọng nói, và vi phạm điều
khoản của chính các model này.
