---
name: clone-giong-noi
description: Clone giọng nói tiếng Việt tự nhiên, giống giọng gốc, bằng VieNeu-TTS v3 Turbo - clone tức thì từ clip 3-8 giây hoặc fine-tune LoRA để bám giọng sát hơn. Dùng khi người dùng muốn giả giọng, nhân bản giọng nói, lồng tiếng, đọc văn bản/sách nói tiếng Việt, hoặc nhắc tới VieNeu, voice cloning, TTS tiếng Việt, ebook2audiobook.
---

# Clone giọng nói tiếng Việt (VieNeu-TTS v3 Turbo)

Dùng [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) (Apache-2.0) — model
tiếng Việt **native**, train từ đầu trên 10.000+ giờ, xuất **48 kHz**, clone
giọng từ clip **3–8 giây**, chạy được **CPU real-time** (ONNX, không cần torch).

## ⚠️ Về yêu cầu "clone giống hệt" — đọc trước

Nói thẳng: **không có bản mã nguồn mở nào clone được giống hệt 100%.** Có 3 mức,
chọn theo mức bạn chấp nhận được:

| Mức | Cần gì | Độ giống | Mã nguồn mở? |
|---|---|---|---|
| **1. Clone tức thì** | clip 3–8 giây | Tự nhiên, nghe ra là giọng đó, nhưng chưa trùng khít | ✅ Có |
| **2. Fine-tune LoRA** | 10–30 phút audio sạch + GPU ~6GB | **Bám giọng chặt hơn hẳn mức 1** — cao nhất trong open source | ✅ Có |
| **3. VieNeu v4** | trả phí | "Near-original fidelity" — sát giọng gốc nhất | ❌ **Không** |

**v4 cố tình không mở mã nguồn.** Tác giả nói rõ trong README: vì khả năng clone
quá mạnh và nguy cơ bị lạm dụng, v4 là hàng độc quyền, chỉ dùng qua API trả phí
tại [vieneu.io](https://www.vieneu.io). v3 Turbo là bản mở mới nhất.

→ **Muốn giống nhất mà vẫn miễn phí: làm mức 2 (fine-tune LoRA).** Skill này có
sẵn script cho cả hai mức.

## Cài đặt

```bash
bash .claude/skills/clone-giong-noi/scripts/install.sh
```

Script tự cài `uv`, clone repo về `~/VieNeu-TTS`, rồi chọn bản phù hợp phần cứng:

- **Có GPU NVIDIA** → bản CUDA (PyTorch). **Bắt buộc nếu muốn fine-tune LoRA.**
- **Không có GPU / macOS** → bản ONNX torch-free. Trên Apple Silicon đây là bản
  **nhanh nhất**, nhanh hơn cả MPS.

Dùng `uv sync` chứ không phải `pip install` — `uv` khoá đúng bản ONNX Runtime đã
tối ưu, chạy nhanh hơn đáng kể.

## Mức 1 — Clone tức thì

```bash
cd ~/VieNeu-TTS
uv run python ~/haodavines/.claude/skills/clone-giong-noi/scripts/clone.py \
    --text bai-viet.txt --ref giong-mau.wav -o ket-qua.wav
```

| Tham số | Ý nghĩa |
|---|---|
| `--text` | File `.txt` hoặc chuỗi text trực tiếp |
| `--ref` | Clip giọng mẫu **3–8 giây** (tự khử ồn, tự cắt) |
| `--voice` | Dùng 1 trong 25 giọng dựng sẵn thay vì clone |
| `-o` | File xuất ra |
| `--nghi` | Khoảng lặng giữa các đoạn, giây (mặc định `0.4`) |
| `--backbone` | Thư mục model đã fine-tune (mức 2) |
| `--int8` | CPU nhanh hơn ~1.6×, **chỉ dùng nếu CPU có VNNI**, không thì audio méo |
| `--temperature` | Độ biến thiên giọng (mặc định `0.8`). **Giảm `0.6`–`0.7` để bám giọng mẫu sát hơn** |
| `--repetition-penalty` | Chống lặp từ khi đọc dài (mặc định `1.2`). Tăng `1.3`–`1.5` nếu bị lặp |
| `--list-voices` | Xem 25 giọng dựng sẵn (Bắc/Trung/Nam) |

Script tự tách văn bản theo đoạn (dòng trống), đọc từng đoạn rồi ghép lại với
khoảng lặng — giữ giọng đồng nhất xuyên suốt bài dài.

Hoặc dùng giao diện web: `cd ~/VieNeu-TTS && uv run vieneu-web` → `http://127.0.0.1:7860`

## Mức 2 — Fine-tune LoRA (để giống sát nhất)

**Cần GPU NVIDIA ~6GB VRAM.** Không có GPU thì dùng
[Colab](https://colab.research.google.com/drive/1b9PO-lcGZX9pEkEwQmu8MfhSnjxKrALW).

Chuẩn bị dữ liệu — **10–30 phút audio sạch của MỘT người, 100–300 câu khác nhau**:

```
du-lieu-giong/
  metadata.csv      mỗi dòng:  ten_file.wav|nội dung câu đọc
  raw_audio/        các file audio được nhắc trong metadata.csv
```

Yêu cầu: mỗi clip **1–20 giây**, một người nói, không nhạc nền, ít vang, và text
phải **khớp đúng từng dấu câu** với audio.

```bash
bash .claude/skills/clone-giong-noi/scripts/finetune.sh giong_toi ./du-lieu-giong ./mau.wav
```

Script chạy đủ 4 bước: cài phụ thuộc → chuẩn bị dữ liệu → train LoRA → đóng gói
giọng vào model. Xong thì dùng lại `clone.py` với `--backbone`:

```bash
uv run python .../clone.py --text bai.txt --ref mau.wav \
    --backbone finetune/output/giong_toi/merged -o ket-qua.wav
```

**Số lượng câu đa dạng quan trọng hơn tổng thời lượng.** Ít dữ liệu thì rủi ro là
overfit chứ không phải thiếu — theo dõi eval loss, ngừng giảm là dừng.

Trong log train, để ý `acc_cb0`: phải ở mức **0.2–0.4 ngay từ bước đầu** rồi tăng
dần. Nếu gần 0 thì dữ liệu sai — thường là text không khớp audio.

⚠️ Model đã fine-tune **chỉ chạy trên GPU (PyTorch)**. Đường CPU/ONNX dùng đồ thị
export sẵn của model gốc nên không nhận model fine-tune.

## Mẹo cho giọng tự nhiên

- **Clip mẫu là yếu tố quyết định.** Giọng đọc đều, rõ, không nhạc nền. Chất
  lượng clip mẫu ảnh hưởng nhiều hơn mọi tham số khác.
- **Phong cách đọc đi theo clip mẫu.** Muốn giọng đọc truyện thì clip mẫu phải là
  đọc truyện. Tham số `style` đã bị bỏ ở v3 Turbo và không còn tác dụng.
- **Chèn cảm xúc thẳng vào text** (thử nghiệm): `[cười]`, `[thở dài]`, `[hắng giọng]`.
  ```
  Nghe hay quá đi [cười]. Để mình nói tiếp [hắng giọng].
  ```
- **Chuẩn hoá số và viết tắt trước khi đọc**: `2025` → `hai nghìn không trăm hai
  mươi lăm`, `TP.HCM` → `Thành phố Hồ Chí Minh`.
- **Tách đoạn bằng dòng trống** trong file `.txt` để script chèn khoảng lặng
  đúng chỗ.
- **Muốn bám giọng mẫu sát hơn mà chưa fine-tune**: hạ `--temperature` xuống
  `0.6`–`0.7`. Giọng sẽ đều và giống mẫu hơn, đổi lại bớt biến hoá.
- **Watermark tắt mặc định.** Muốn nhúng watermark Perth để truy vết về sau (dùng
  có trách nhiệm): `uv pip install "vieneu[watermark]"`.

## Khắc phục sự cố

| Triệu chứng | Xử lý |
|---|---|
| Audio bị méo, rè | Bỏ `--int8` — CPU của bạn không có VNNI |
| Giọng chưa đủ giống | Đây là giới hạn của clone tức thì. Lên mức 2 (fine-tune LoRA) |
| Quá chậm trên CPU | Thử `--int8` (nếu CPU hỗ trợ), hoặc `Vieneu(mode="v3nano")` — nhanh hơn ~3× nhưng chất lượng thấp hơn, 24 kHz |
| Tiếng Anh xen kẽ đọc sai | v3 Turbo hỗ trợ song ngữ En-Vi. Nếu dùng v3 Nano thì Nano yếu hẳn phần tiếng Anh |
| `acc_cb0` gần 0 khi train | Text trong `metadata.csv` không khớp audio. Kiểm tra lại từng dòng |
| Hết VRAM khi train | Thêm `--grad-checkpoint`, hoặc giảm `--batch-size` |

## Cần đọc thẳng .epub / .pdf?

VieNeu-TTS nhận text thuần. Muốn đọc thẳng ebook và tự tách chương, xuất `.m4b`,
dùng ebook2audiobook — nhưng **chất lượng tiếng Việt kém hơn hẳn**. Chi tiết và
scripts (`e2a-install.sh`, `e2a-doc.sh`) trong [reference.md](reference.md).

## Lưu ý pháp lý

Chỉ clone giọng khi **có sự đồng ý của chủ giọng**. Chính tác giả VieNeu đã giữ
kín bản v4 vì lo ngại lạm dụng — hãy tôn trọng điều đó. Dùng giọng người thật
không xin phép có thể vi phạm quyền nhân thân về giọng nói.
