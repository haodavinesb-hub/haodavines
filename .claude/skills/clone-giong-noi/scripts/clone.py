#!/usr/bin/env python3
"""Clone giọng nói tiếng Việt và đọc văn bản dài bằng VieNeu-TTS v3 Turbo.

Ví dụ:
    # Clone tức thì từ clip 3-8 giây
    python clone.py --text bai-viet.txt --ref giong-mau.wav -o ket-qua.wav

    # Đọc một câu ngắn
    python clone.py --text "Xin chào các bạn." --ref giong-mau.wav

    # Dùng giọng có sẵn thay vì clone
    python clone.py --text bai-viet.txt --voice "Minh Quân"

    # Xem 25 giọng dựng sẵn
    python clone.py --list-voices

    # Dùng model đã fine-tune LoRA (giống hệt hơn)
    python clone.py --text bai.txt --ref giong.wav --backbone finetune/output/my_voice/merged

Chạy trong môi trường của VieNeu-TTS:
    cd ~/VieNeu-TTS && uv run python /duong/dan/clone.py ...
"""
import argparse
import os
import re
import sys
import time

SAMPLE_RATE = 48_000  # v3 Turbo xuất 48 kHz


def doc_van_ban(nguon: str) -> str:
    """Nhận đường dẫn file hoặc chuỗi text trực tiếp."""
    if os.path.isfile(nguon):
        with open(nguon, encoding="utf-8") as f:
            return f.read()
    return nguon


def tach_doan(text: str) -> list[str]:
    """Tách theo đoạn văn (dòng trống). Giữ nguyên câu, không cắt giữa chừng.

    infer() của VieNeu tự chia chunk bên trong, nhưng tách sẵn theo đoạn cho ta
    kiểm soát được khoảng lặng giữa các đoạn — nghe tự nhiên hơn khi đọc dài.
    """
    doan = [d.strip() for d in re.split(r"\n\s*\n", text)]
    return [d for d in doan if d]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Clone giọng nói tiếng Việt và đọc văn bản dài (VieNeu-TTS v3 Turbo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--text", help="File văn bản (.txt) hoặc chuỗi text trực tiếp")
    p.add_argument("--ref", help="Clip giọng mẫu 3-8 giây để clone")
    p.add_argument("--voice", help="Tên giọng dựng sẵn (thay cho --ref)")
    p.add_argument("-o", "--out", default="ket-qua.wav", help="File audio xuất ra")
    p.add_argument("--list-voices", action="store_true", help="Liệt kê các giọng dựng sẵn")
    p.add_argument("--no-denoise", action="store_true",
                   help="Bỏ khử ồn clip mẫu (dùng khi clip đã sạch sẵn)")
    p.add_argument("--nghi", type=float, default=0.4,
                   help="Khoảng lặng giữa các đoạn, tính bằng giây (mặc định 0.4)")
    p.add_argument("--backbone", help="Đường dẫn model đã fine-tune LoRA (thư mục merged)")
    p.add_argument("--int8", action="store_true",
                   help="CPU: nhanh hơn ~1.6x nhưng CẦN CPU có VNNI, không thì audio bị méo")
    # Các tham số chỉnh độ tự nhiên / ổn định (mặc định lấy đúng của VieNeu v3 Turbo)
    p.add_argument("--temperature", type=float, default=0.8,
                   help="Độ biến thiên giọng (mặc định 0.8). Giảm xuống 0.6-0.7 cho đều và bám giọng hơn")
    p.add_argument("--repetition-penalty", type=float, default=1.2,
                   help="Chống lặp từ khi đọc dài (mặc định 1.2). Tăng 1.3-1.5 nếu bị lặp")
    p.add_argument("--max-chars", type=int, default=256,
                   help="Số ký tự tối đa mỗi chunk nội bộ (mặc định 256)")
    args = p.parse_args()

    try:
        import numpy as np
        from vieneu import Vieneu
    except ImportError as e:
        print(f"LỖI: thiếu thư viện ({e}).", file=sys.stderr)
        print("Chạy trong môi trường VieNeu: cd ~/VieNeu-TTS && uv run python clone.py ...",
              file=sys.stderr)
        return 1

    kwargs = {}
    if args.backbone:
        kwargs["backbone_repo"] = args.backbone
    if args.int8:
        kwargs["precision"] = "int8"

    print("==> Đang nạp VieNeu-TTS v3 Turbo...")
    print("    (lần chạy đầu sẽ tải model từ Hugging Face, mất vài phút)")
    try:
        tts = Vieneu(**kwargs)
    except Exception as e:
        loi = str(e)
        if "huggingface.co" in loi or "ProxyError" in loi or "Max retries" in loi:
            print("\nLỖI: không tải được model từ Hugging Face.", file=sys.stderr)
            print("Kiểm tra theo thứ tự:", file=sys.stderr)
            print("  1. Máy có vào được https://huggingface.co không?", file=sys.stderr)
            print("  2. Đang sau proxy/firewall chặn HF? Đặt HTTPS_PROXY cho đúng.", file=sys.stderr)
            print("  3. Máy offline? Tải model trước ở máy có mạng rồi copy cache sang:",
                  file=sys.stderr)
            print("     huggingface-cli download pnnbao-ump/VieNeu-TTS-v3-Turbo", file=sys.stderr)
            print("     rồi copy ~/.cache/huggingface sang máy này và đặt HF_HUB_OFFLINE=1",
                  file=sys.stderr)
            return 2
        raise

    if args.list_voices:
        voices = tts.list_preset_voices()
        print(f"\n{len(voices)} giọng dựng sẵn:")
        for label, voice_id in voices:
            print(f"  - {label}  ({voice_id})")
        return 0

    if not args.text:
        p.error("cần --text (file hoặc chuỗi), hoặc dùng --list-voices")
    if not args.ref and not args.voice:
        p.error("cần --ref (clip giọng mẫu) hoặc --voice (giọng dựng sẵn)")
    if args.ref and not os.path.isfile(args.ref):
        print(f"LỖI: không thấy clip giọng mẫu: {args.ref}", file=sys.stderr)
        return 1

    # Nạp giọng clone MỘT LẦN rồi dùng theo tên: trích speaker profile một lần
    # thay vì lặp lại cho từng đoạn, và giữ giọng đồng nhất xuyên suốt.
    if args.ref:
        ten_giong = "giong-clone"
        print(f"==> Đang clone giọng từ: {args.ref}")
        tts.add_voice(ten_giong, args.ref, denoise=not args.no_denoise)
    else:
        ten_giong = args.voice
        print(f"==> Dùng giọng dựng sẵn: {ten_giong}")

    doan_list = tach_doan(doc_van_ban(args.text))
    print(f"==> {len(doan_list)} đoạn cần đọc\n")

    lang = np.zeros(int(SAMPLE_RATE * args.nghi), dtype=np.float32)
    phan_audio = []
    t0 = time.time()

    for i, doan in enumerate(doan_list, 1):
        xem_truoc = doan[:60] + ("..." if len(doan) > 60 else "")
        print(f"  [{i}/{len(doan_list)}] {xem_truoc}")
        phan_audio.append(np.asarray(
            tts.infer(
                doan,
                voice=ten_giong,
                temperature=args.temperature,
                repetition_penalty=args.repetition_penalty,
                max_chars=args.max_chars,
            ),
            dtype=np.float32,
        ))
        if i < len(doan_list):
            phan_audio.append(lang)

    audio = np.concatenate(phan_audio)
    tts.save(audio, args.out)

    thoi_gian = time.time() - t0
    thoi_luong = len(audio) / SAMPLE_RATE
    rtf = thoi_gian / thoi_luong if thoi_luong else 0
    print(f"\n==> Đã lưu: {args.out}")
    print(f"    Thời lượng: {thoi_luong:.1f}s | Xử lý mất: {thoi_gian:.1f}s | RTF: {rtf:.3f}")
    if rtf > 1:
        print(f"    (chậm hơn real-time {rtf:.1f}x — dùng GPU sẽ nhanh hơn nhiều)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
