# haodavines

## Skills

| Skill | Mô tả |
|---|---|
| [`clone-giong-noi`](.claude/skills/clone-giong-noi/SKILL.md) | Clone giọng nói tiếng Việt tự nhiên bằng [VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS) — clone tức thì từ clip 3–8 giây, hoặc fine-tune LoRA để bám giọng sát hơn |

## Chan Hair SEO

[`chanhair-seo/`](chanhair-seo/README.md): tạo các trang chuẩn SEO "cắt tóc layer TP.HCM" cho chanhair.vn, gồm trang dịch vụ chính và 11 trang kiểu tóc layer. Bỏ ảnh vào `chanhair-seo/anh/<kiểu>/` rồi chạy `python3 chanhair-seo/build.py`.

## Clone giọng nói

### Cách nhanh nhất — Colab, không cần cài

[**▶ Mở notebook trên Colab**](https://colab.research.google.com/github/haodavinesb-hub/haodavines/blob/claude/github-voice-synthesis-projects-uzr588/.claude/skills/clone-giong-noi/notebooks/clone-giong-colab.ipynb)

### Cài trên máy

```bash
# 1. Cài đặt (tự chọn bản CUDA hay ONNX theo phần cứng)
bash .claude/skills/clone-giong-noi/scripts/install.sh

# 2. Clone tức thì từ clip 3-8 giây
cd ~/VieNeu-TTS
uv run python ~/haodavines/.claude/skills/clone-giong-noi/scripts/clone.py \
    --text bai-viet.txt --ref giong-mau.wav -o ket-qua.wav

# 3. Muốn giống sát hơn: fine-tune LoRA (cần GPU ~6GB, 10-30 phút audio sạch)
bash .claude/skills/clone-giong-noi/scripts/finetune.sh giong_toi ./du-lieu-giong ./mau.wav
```

Giao diện web: `cd ~/VieNeu-TTS && uv run vieneu-web` → `http://127.0.0.1:7860`

Chi tiết: [SKILL.md](.claude/skills/clone-giong-noi/SKILL.md) ·
[reference.md](.claude/skills/clone-giong-noi/reference.md)
