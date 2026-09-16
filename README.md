# haodavines

## Skills

| Skill | Mô tả |
|---|---|
| [`clone-giong-noi`](.claude/skills/clone-giong-noi/SKILL.md) | Clone giọng nói và đọc văn bản dài thành audiobook bằng [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook), có hướng dẫn riêng cho tiếng Việt |

### Dùng skill clone giọng nói

```bash
# 1. Cài đặt (lần đầu, tải vài GB)
bash .claude/skills/clone-giong-noi/scripts/install.sh
cd ~/ebook2audiobook && ./ebook2audiobook.sh --help

# 2. Đọc văn bản bằng giọng clone
bash .claude/skills/clone-giong-noi/scripts/doc.sh bai-viet.txt giong-mau.wav
```

Chi tiết: [SKILL.md](.claude/skills/clone-giong-noi/SKILL.md) ·
[reference.md](.claude/skills/clone-giong-noi/reference.md)
