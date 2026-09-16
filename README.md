# haodavines

## Skills

| Skill | Mô tả |
|---|---|
| [`clone-giong-noi`](.claude/skills/clone-giong-noi/SKILL.md) | Clone giọng nói tiếng Việt tự nhiên bằng [VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS) — clone tức thì từ clip 3–8 giây, hoặc fine-tune LoRA để bám giọng sát hơn |

### Dùng skill clone giọng nói

```bash
# 1. Cài đặt
bash .claude/skills/clone-giong-noi/scripts/install.sh

# 2. Clone tức thì từ clip 3-8 giây
cd ~/VieNeu-TTS
uv run python ~/haodavines/.claude/skills/clone-giong-noi/scripts/clone.py \
    --text bai-viet.txt --ref giong-mau.wav -o ket-qua.wav

# 3. Muốn giống sát hơn: fine-tune LoRA (cần GPU ~6GB, 10-30 phút audio sạch)
bash .claude/skills/clone-giong-noi/scripts/finetune.sh giong_toi ./du-lieu-giong ./mau.wav
```

Chi tiết: [SKILL.md](.claude/skills/clone-giong-noi/SKILL.md) ·
[reference.md](.claude/skills/clone-giong-noi/reference.md)
