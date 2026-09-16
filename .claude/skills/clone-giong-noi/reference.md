# Tham khảo chi tiết

## Engine nào hỗ trợ ngôn ngữ nào

Trích từ `lib/conf_models.py` của ebook2audiobook v26.9.x.

| Engine | Ngôn ngữ | Clone giọng thật? | Tiếng Việt? |
|---|---|---|---|
| **XTTS** (XTTSv2) | 17: `ara ces deu eng fra hin hun ita jpn kor nld pol por rus spa tur zho` | ✅ Có (zero-shot gốc) | ❌ **Không** |
| **FAIRSEQ** (Meta MMS) | 1100+ ngôn ngữ, gồm `vie` | ⚠️ Gián tiếp (qua voice conversion) | ✅ Có |
| **BARK** | ít | ✅ | ❌ |
| **VITS** | tuỳ checkpoint | ⚠️ Gián tiếp | ❌ |
| **GLOWTTS** | `eng ukr tur ita fas bel` | ⚠️ Gián tiếp | ❌ |
| **TACOTRON** | `deu eng fra spa` | ⚠️ Gián tiếp | ❌ |
| **YOURTTS** | ít | ⚠️ Gián tiếp | ❌ |

Các engine trong `tts_engines_with_inner_speaker` (PIPER, VITS, FAIRSEQ,
GLOWTTS, TACOTRON, YOURTTS) đều dùng **giọng nội bộ cố định**. Khi bạn truyền
`--voice`, code bật cờ `use_zs = True` rồi chạy thêm một bước **voice
conversion** để ép sang giọng mẫu.

## Đổi model voice conversion (có thể cải thiện tiếng Việt)

Mặc định là `knnvc` (16kHz). Có 4 lựa chọn trong `TTS_VOICE_CONVERSION`:

| Model | Samplerate | Ghi chú |
|---|---|---|
| `knnvc` | 16000 | Mặc định |
| `freevc24` | 24000 | Samplerate cao hơn, thường trong hơn |
| `openvoice_v1` | 22050 | |
| `openvoice_v2` | 22050 | Thường giữ được sắc giọng tốt nhất |

Đổi bằng cách sửa `lib/conf_models.py` trong thư mục cài đặt:

```python
# Dòng ~64
default_vc_model = TTS_VOICE_CONVERSION['openvoice_v2']['path']
```

**Đáng thử khi giọng tiếng Việt clone ra nghe không giống mẫu.** Chưa có lựa
chọn nào là "đúng" — nên thử cả `freevc24` và `openvoice_v2` rồi tự nghe so sánh.

## Chuẩn hoá text tiếng Việt trước khi đọc

Đây là nguyên nhân lỗi phổ biến nhất. FAIRSEQ/MMS không có bước chuẩn hoá
tiếng Việt, nên phải tự làm trước:

| Viết trong file | Nên đổi thành |
|---|---|
| `2025` | `hai nghìn không trăm hai mươi lăm` |
| `15/3/2024` | `ngày mười lăm tháng ba năm hai nghìn không trăm hai mươi tư` |
| `TP.HCM` | `Thành phố Hồ Chí Minh` |
| `150.000đ` | `một trăm năm mươi nghìn đồng` |
| `km/h` | `ki lô mét trên giờ` |
| `AI`, `GDP` | `ây ai`, `giê đê pê` |

## Đọc đoạn dài 1–2 phút cho mượt

- 250–400 từ ≈ 1–2 phút audio.
- Chèn `[pause]` giữa các đoạn văn, `[break]` giữa các câu dài.
- Dùng **cùng một file giọng mẫu** cho toàn bộ văn bản, nếu không giọng sẽ
  lệch dần giữa các đoạn.
- Nếu bị lặp từ hoặc trôi giọng: tăng `--repetition_penalty` (mặc định `2.0`),
  giảm `--temperature` (mặc định `0.75`), hoặc cắt nhỏ file nguồn.
- `.epub` và `.mobi` cho kết quả tách chương tự động tốt nhất. `.txt` thì bạn
  tự chia đoạn bằng dòng trống.

## Lựa chọn thay thế cho tiếng Việt

Nếu chất lượng tiếng Việt của ebook2audiobook không đạt, cân nhắc:

| Dự án | Ưu điểm | Nhược điểm |
|---|---|---|
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) (Apache-2.0) | Native tiếng Việt, clone từ clip **3–8 giây**, 24kHz, chạy CPU real-time, fine-tune LoRA chỉ ~6GB VRAM. Bản v3 Turbo có sliding-window repetition penalty chống trôi khi đọc dài | Không đọc thẳng `.epub`/`.pdf` |
| [VieNeu-Audio](https://github.com/NTQD/VieNeu-Audio) (MIT) | Pipeline audiobook dựng trên VieNeu-TTS: chuẩn hoá số/đơn vị, chia chunk ~250 từ, ghép lại | Repo rất mới, gần như chưa có cộng đồng |
| [viXTTS](https://github.com/thinhlpg/vixtts-demo) | XTTS fine-tune tiếng Việt, có Colab chạy ngay | Phải tự chia đoạn cho văn bản dài |
| [F5-TTS-Vietnamese-ViVoice](https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice) | Chất lượng giọng tốt | Giới hạn ~30s mỗi lần sinh, phải tự chunk |

**Tóm lại:** ebook2audiobook mạnh ở khâu *pipeline sách nói* (đọc thẳng ebook,
tách chương, xuất `.m4b`, đa ngôn ngữ). VieNeu-TTS mạnh ở khâu *chất lượng
giọng tiếng Việt*. Nếu cần cả hai: dùng VieNeu-Audio, hoặc dùng
ebook2audiobook để trích text rồi đưa sang VieNeu-TTS.

## Nguồn

- Repo: https://github.com/DrewThomasson/ebook2audiobook (Apache-2.0)
- Cấu hình engine đã kiểm chứng: `lib/conf_models.py`
- Đường voice conversion: `lib/classes/tts_engines/fairseq.py`
