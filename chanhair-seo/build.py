#!/usr/bin/env python3
"""Sinh các trang SEO "cắt tóc layer" cho chanhair.vn.

    python3 build.py              # tạo lại toàn bộ dist/
    python3 -m http.server -d dist 8000   # xem thử ở http://localhost:8000/cat-toc-layer-ho-chi-minh/

Dữ liệu: data/site.json (thông tin salon + trang dịch vụ), data/styles.json (từng kiểu layer).
Ảnh: bỏ vào anh/<slug>/ — script tự đổi tên chuẩn SEO, nén WebP, thêm alt.
Kết quả: dist/ có cấu trúc thư mục trùng đường dẫn trên web, kèm sitemap và seo-map.csv.
"""
import csv
import html
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ANH = ROOT / "anh"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"  # ghi nhớ ảnh đã nén, không cần đưa lên web
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MO_TA = "_mo-ta.txt"  # file tuỳ chọn trong mỗi thư mục ảnh: "ten-file.jpg: mô tả ảnh"
LANDING_IMG_DIR = "cat-toc-layer"  # ảnh riêng cho trang dịch vụ chính
SIZES = (1200, 600)
SOCIAL_NAMES = {"instagram": "Instagram", "facebook": "Facebook", "tiktok": "TikTok", "youtube": "YouTube"}  # bản lớn + bản nhỏ cho điện thoại (srcset)

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
try:
    import pillow_heif  # ảnh HEIC từ iPhone

    pillow_heif.register_heif_opener()
except ImportError:
    pass

warnings = []


def warn(msg):
    warnings.append(msg)


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(text):
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_json(name):
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- ảnh


def read_captions(folder):
    path = folder / MO_TA
    caps = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                name, cap = line.split(":", 1)
                caps[name.strip()] = cap.strip()
    return caps


def process_images(folder_name, seo_name, alt_base):
    """Nén + đổi tên ảnh trong anh/<folder_name>/, trả về danh sách ảnh để chèn vào trang."""
    src_dir = ANH / folder_name
    src_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in IMG_EXT)
    caps = read_captions(src_dir)
    out_rel = f"anh/toc-layer/{folder_name}"
    out_dir = DIST / out_rel
    out_dir.mkdir(parents=True, exist_ok=True)
    # nhớ ảnh nào đã nén từ file gốc nào, để thêm/xoá/đổi ảnh không làm lệch số thứ tự
    manifest_path = CACHE / f"{folder_name}.json"
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {}
    images = []
    for n, src in enumerate(files, 1):
        caption = caps.get(src.name, "")
        alt = f"{alt_base} - {caption}" if caption else f"{alt_base} - mẫu {n}"
        base = f"{seo_name}-{n}"
        stamp = f"{src.name}|{src.stat().st_mtime_ns}|{src.stat().st_size}"
        if Image is None:
            dest = out_dir / f"{base}{src.suffix.lower()}"
            shutil.copy2(src, dest)
            manifest[dest.name] = {"nguon": stamp}
            images.append({"src": f"/{out_rel}/{dest.name}", "small": None, "w": None, "h": None,
                           "alt": alt, "caption": caption})
            continue
        big, small = f"{base}.webp", f"{base}-{SIZES[1]}w.webp"
        cached = old.get(big)
        if cached and cached["nguon"] == stamp and (out_dir / big).exists() and (out_dir / small).exists():
            info = cached
        else:
            try:
                img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            except Exception as e:  # ảnh hỏng / định dạng lạ (HEIC khi thiếu pillow-heif)
                warn(f"Không đọc được ảnh {src.relative_to(ROOT)}: {e}")
                continue
            sizes = []
            for width, name in zip(SIZES, (big, small)):
                copy = img.copy()
                copy.thumbnail((width, width * 3))
                copy.save(out_dir / name, "WEBP", quality=80, method=5)  # không ghi EXIF/GPS
                sizes.append(copy.size)
            info = {"nguon": stamp, "w": sizes[0][0], "h": sizes[0][1], "small_w": sizes[1][0]}
        manifest[big] = info
        manifest[small] = {"nguon": stamp}
        images.append({"src": f"/{out_rel}/{big}",
                       "small": f"/{out_rel}/{small}" if info["small_w"] < info["w"] else None,
                       "small_w": info["small_w"], "w": info["w"], "h": info["h"],
                       "alt": alt, "caption": caption})
    for stale in out_dir.iterdir():  # ảnh đã bị xoá khỏi thư mục gốc
        if stale.name not in manifest:
            stale.unlink()
    CACHE.mkdir(exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    return images


def img_tag(im, eager=False, sizes="(max-width: 700px) 100vw, 600px"):
    attrs = [f'src="{esc(im["src"])}"', f'alt="{esc(im["alt"])}"']
    if im.get("small"):
        attrs.append(f'srcset="{esc(im["small"])} {im["small_w"]}w, {esc(im["src"])} {im["w"]}w"')
        attrs.append(f'sizes="{sizes}"')
    if im.get("w"):
        attrs.append(f'width="{im["w"]}" height="{im["h"]}"')
    attrs.append('fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    return f"<img {' '.join(attrs)}>"


def gallery(images):
    if not images:
        return ""
    items = []
    for im in images:
        cap = f"<figcaption>{esc(im['caption'])}</figcaption>" if im["caption"] else ""
        items.append(f"<figure>{img_tag(im)}{cap}</figure>")
    return f'<div class="gallery">{"".join(items)}</div>'


# ---------------------------------------------------------------- khối nội dung dùng chung


def paragraphs(items):
    return "".join(f"<p>{esc(p)}</p>" for p in items)


def bullets(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>" if items else ""


def faq_html(faqs):
    if not faqs:
        return ""
    rows = "".join(
        f"<details><summary>{esc(f['q'])}</summary><p>{esc(f['a'])}</p></details>" for f in faqs
    )
    return f'<section id="hoi-dap"><h2>Câu hỏi thường gặp</h2>{rows}</section>'


def faq_schema(faqs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ],
    }


def breadcrumb_html(crumbs):
    parts = []
    for i, (name, url) in enumerate(crumbs):
        last = i == len(crumbs) - 1
        parts.append(f'<span aria-current="page">{esc(name)}</span>' if last
                     else f'<a href="{esc(url)}">{esc(name)}</a>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" › ".join(parts)}</nav>'


def breadcrumb_schema(site, crumbs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": site["domain"] + url}
            for i, (name, url) in enumerate(crumbs, 1)
        ],
    }


def cta_html(site, text=None):
    zalo, tel = site["dat_lich"]["zalo"], site["dat_lich"]["dien_thoai"]
    text = text or "Gửi ảnh tóc hiện tại qua Zalo, stylist tư vấn kiểu layer hợp khuôn mặt miễn phí."
    btns = []
    if zalo:
        btns.append(f'<a class="btn" href="https://zalo.me/{esc(zalo)}" rel="nofollow">Đặt lịch qua Zalo</a>')
    if tel:
        btns.append(f'<a class="btn ghost" href="tel:{esc(tel)}">Gọi {esc(pretty_phone(tel))}</a>')
    return f'<aside class="cta"><p>{esc(text)}</p><div class="btns">{"".join(btns)}</div></aside>'


def pretty_phone(tel):
    d = re.sub(r"\D", "", tel)
    return f"{d[:4]} {d[4:7]} {d[7:]}" if len(d) == 10 else tel


def branch_address(b):
    addr = ", ".join(x for x in (b["dia_chi"], b.get("phuong"), b["thanh_pho"]) if x)
    return f"{addr} ({b['dia_chi_cu']})" if b.get("dia_chi_cu") else addr


def branches_html(site, only_city=None):
    rows = []
    for b in site["chi_nhanh"]:
        if only_city and b["thanh_pho"] != only_city:
            continue
        maps = (f' · <a href="{esc(b["google_maps"])}" rel="nofollow noopener" target="_blank">Chỉ đường</a>'
                if b.get("google_maps") else "")
        hours = f"<br>Giờ mở cửa: {esc(b['gio_mo_cua'])}" if b.get("gio_mo_cua") else ""
        tel = b.get("dien_thoai") or site["dat_lich"]["dien_thoai"]
        tel_html = f'<br>Điện thoại: <a href="tel:{esc(tel)}">{esc(pretty_phone(tel))}</a>' if tel else ""
        rows.append(f"<li><strong>{esc(b['ten'])}</strong><br>{esc(branch_address(b))}{hours}{tel_html}{maps}</li>")
    return '<ul class="branches">' + "".join(rows) + "</ul>"


def base_schema(site):
    """WebSite + mỗi chi nhánh là một HairSalon — Google dùng để nối trang web với Google Maps."""
    out = [{"@type": "WebSite", "@id": site["domain"] + "/#website", "url": site["domain"] + "/",
            "name": site["ten"], "inLanguage": "vi"}]
    for b in site["chi_nhanh"]:
        s = {
            "@type": "HairSalon",
            "@id": f"{site['domain']}/#{b['id']}",
            "name": b["ten"],
            "url": site["domain"] + "/",
            "telephone": b.get("dien_thoai") or site["dat_lich"]["dien_thoai"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": b["dia_chi"],
                "addressLocality": b.get("phuong", ""),
                "addressRegion": b["thanh_pho"],
                "addressCountry": "VN",
            },
            "sameAs": [u for u in [b.get("facebook"), *site["mang_xa_hoi"].values()] if u],
        }
        if b.get("opening_hours"):
            s["openingHours"] = b["opening_hours"]
        if b.get("lat") and b.get("lng"):
            s["geo"] = {"@type": "GeoCoordinates", "latitude": b["lat"], "longitude": b["lng"]}
        if b.get("google_maps"):
            s["hasMap"] = b["google_maps"]
        if site.get("logo"):
            s["image"] = site["domain"] + site["logo"]
        if site.get("khoang_gia"):
            s["priceRange"] = site["khoang_gia"]
        out.append(s)
    return out


# ---------------------------------------------------------------- khung trang

CSS = """
:root{--bg:#faf7f4;--card:#fff;--ink:#1f1a17;--muted:#6b615a;--line:#e9e1da;--accent:#a8664b;--accent-ink:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--accent)}
header.top{background:var(--card);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:12px;padding-bottom:12px}
.logo{font-weight:700;font-size:20px;letter-spacing:.5px;color:var(--ink);text-decoration:none}
header.top nav a{margin-left:16px;color:var(--ink);text-decoration:none;font-size:15px}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}
.crumbs{font-size:14px;color:var(--muted);margin:16px 0}
.crumbs a{color:var(--muted)}
h1{font-size:clamp(28px,5vw,40px);line-height:1.2;margin:8px 0 12px}
h2{font-size:clamp(22px,3.6vw,28px);line-height:1.3;margin:40px 0 12px}
h3{font-size:19px;margin:20px 0 6px}
.lead{font-size:19px;color:var(--muted)}
.hero img{display:block;width:auto;max-width:100%;height:auto;max-height:72vh;margin:0 auto;border-radius:14px}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.gallery figure{margin:0}
.gallery img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;border-radius:12px;display:block;background:var(--line)}
figcaption{font-size:14px;color:var(--muted);margin-top:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;padding:0;list-style:none}
.cards li{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.cards a{display:block;color:var(--ink);text-decoration:none;height:100%}
.cards img{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;display:block}
.cards .txt{padding:12px 14px 16px}
.cards h3{margin:0 0 4px;font-size:18px}
.cards p{margin:0;color:var(--muted);font-size:15px}
.steps{counter-reset:s;list-style:none;padding:0}
.steps li{counter-increment:s;position:relative;padding:0 0 14px 44px}
.steps li:before{content:counter(s);position:absolute;left:0;top:0;width:30px;height:30px;border-radius:50%;background:var(--accent);color:var(--accent-ink);display:grid;place-items:center;font-weight:700;font-size:15px}
table{width:100%;border-collapse:collapse;background:var(--card)}
td,th{border:1px solid var(--line);padding:10px 12px;text-align:left}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:10px 0}
summary{font-weight:600;cursor:pointer}
details p{margin:8px 0 0}
.cta{background:var(--ink);color:#fff;border-radius:16px;padding:22px;margin:36px 0}
.cta p{margin:0 0 14px;font-size:18px}
.btns{display:flex;flex-wrap:wrap;gap:10px}
.btn{display:inline-block;background:var(--accent);color:var(--accent-ink);text-decoration:none;padding:12px 20px;border-radius:999px;font-weight:600}
.btn.ghost{background:transparent;color:#fff;border:1px solid #fff}
.branches{padding-left:18px}
.branches li{margin-bottom:12px}
.related{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}
.related a{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 14px;text-decoration:none;color:var(--ink)}
footer{border-top:1px solid var(--line);margin-top:48px;padding:24px 0 96px;font-size:15px;color:var(--muted)}
.sticky{position:fixed;left:0;right:0;bottom:0;display:flex;gap:8px;padding:10px 16px;background:rgba(255,255,255,.96);border-top:1px solid var(--line)}
.sticky .btn{flex:1;text-align:center}
.sticky .btn.ghost{color:var(--ink);border-color:var(--ink)}
@media(min-width:800px){.sticky{display:none}footer{padding-bottom:24px}}
@media(max-width:560px){header.top nav a:not(:last-child){display:none}}
""".strip()


def page(site, *, path, title, desc, crumbs, main, schema, og_image=None):
    url = site["domain"] + path
    graph = {"@context": "https://schema.org", "@graph": schema + [breadcrumb_schema(site, crumbs)]}
    ld = json.dumps(graph, ensure_ascii=False, indent=1).replace("</", "<\\/")
    og_img = f'<meta property="og:image" content="{esc(site["domain"] + og_image)}">' if og_image else ""
    zalo, tel = site["dat_lich"]["zalo"], site["dat_lich"]["dien_thoai"]
    sticky = []
    if tel:
        sticky.append(f'<a class="btn ghost" href="tel:{esc(tel)}">Gọi ngay</a>')
    if zalo:
        sticky.append(f'<a class="btn" href="https://zalo.me/{esc(zalo)}" rel="nofollow">Đặt lịch Zalo</a>')
    socials = " · ".join(
        f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(SOCIAL_NAMES.get(k, k))}</a>'
        for k, u in site["mang_xa_hoi"].items() if u
    )
    nav = "".join(f'<a href="{esc(u)}">{esc(n)}</a>' for n, u in site["menu"])
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="{esc(site['ten'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
{og_img}
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="/">{esc(site['ten'])}</a><nav>{nav}</nav></div></header>
<main class="wrap">
{breadcrumb_html(crumbs)}
{main}
</main>
<footer><div class="wrap">
<p><strong>{esc(site['ten'])}</strong> — {esc(site['mo_ta_ngan'])}</p>
{branches_html(site)}
<p>{socials}</p>
</div></footer>
<div class="sticky">{"".join(sticky)}</div>
</body>
</html>
"""


def write(path, content):
    dest = DIST / path.strip("/") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------- các trang


def style_card(style, eager=False):
    img = img_tag(style["images"][0], eager=eager, sizes="(max-width: 560px) 100vw, 300px") if style["images"] else ""
    return (f'<li><a href="{esc(style["path"])}">{img}<div class="txt">'
            f'<h3>{esc(style["ten"])}</h3><p>{esc(style["tom_tat"])}</p></div></a></li>')


def build_landing(site, styles, landing_images):
    L = site["trang_dich_vu"]
    path = L["path"]
    crumbs = [("Trang chủ", "/"), (L["breadcrumb"], path)]
    # ảnh trang chính: ảnh riêng trong anh/cat-toc-layer/; thiếu thì mượn ảnh bìa của các kiểu.
    # Bộ sưu tập lấy ảnh thứ hai của mỗi kiểu để không lặp lại ảnh bìa đã hiện trên thẻ kiểu tóc.
    pics = landing_images or [s["images"][0] for s in styles if s["images"]]
    more = landing_images[1:] + [s["images"][1] for s in styles if len(s["images"]) > 1]
    hero = f'<div class="hero">{img_tag(pics[0], eager=True, sizes="(max-width: 960px) 100vw, 928px")}</div>' if pics else ""
    if L.get("bang_gia"):
        rows = "".join(f"<tr><td>{esc(r['ten'])}</td><td>{esc(r['gia'])}</td></tr>" for r in L["bang_gia"])
        price = f"<table><tr><th>Dịch vụ</th><th>Giá</th></tr>{rows}</table>{paragraphs(L.get('ghi_chu_gia', []))}"
    else:
        price = paragraphs(L["gia_mac_dinh"])
    main = f"""
<h1>{esc(L['h1'])}</h1>
<p class="lead">{esc(L['lead'])}</p>
{hero}
{paragraphs(L['gioi_thieu'])}
{cta_html(site)}
<h2>{esc(L['h2_kieu'])}</h2>
<p>{esc(L['mo_ta_kieu'])}</p>
<ul class="cards">{"".join(style_card(s) for s in styles)}</ul>
<h2>Vì sao nên cắt tóc layer tại {esc(site['ten'])}?</h2>
{bullets(L['ly_do'])}
<h2>Quy trình cắt tóc layer</h2>
<ol class="steps">{"".join(f"<li><strong>{esc(s['buoc'])}</strong> — {esc(s['mo_ta'])}</li>" for s in L['quy_trinh'])}</ol>
{('<h2>Hình ảnh khách cắt layer tại ' + esc(site['ten']) + '</h2>' + gallery(more[:12])) if more else ''}
<h2>Giá cắt tóc layer</h2>
{price}
<h2>Địa chỉ cắt tóc layer tại TP.HCM</h2>
{branches_html(site, only_city=site['thanh_pho_chinh'])}
{faq_html(L['faq'])}
{cta_html(site, L.get('cta'))}
"""
    service = {
        "@type": "Service",
        "name": L["ten_dich_vu"],
        "serviceType": "Cắt tóc layer",
        "description": L["meta_description"],
        "url": site["domain"] + path,
        "areaServed": {"@type": "City", "name": "Thành phố Hồ Chí Minh"},
        "provider": [{"@id": f"{site['domain']}/#{b['id']}"} for b in site["chi_nhanh"]
                     if b["thanh_pho"] == site["thanh_pho_chinh"]],
    }
    if pics:
        service["image"] = [site["domain"] + p["src"] for p in pics[:6]]
    schema = base_schema(site) + [service] + ([faq_schema(L["faq"])] if L["faq"] else [])
    write(path, page(site, path=path, title=L["title"], desc=L["meta_description"], crumbs=crumbs,
                     main=main, schema=schema, og_image=pics[0]["src"] if pics else None))
    return {"url": path, "title": L["title"], "desc": L["meta_description"], "h1": L["h1"],
            "keyword": L["tu_khoa_chinh"], "images": pics[:1] + more}


def build_hub(site, styles):
    H = site["trang_kieu_toc"]
    path = H["path"]
    crumbs = [("Trang chủ", "/"), (H["breadcrumb"], path)]
    main = f"""
<h1>{esc(H['h1'])}</h1>
<p class="lead">{esc(H['lead'])}</p>
<ul class="cards">{"".join(style_card(s, eager=i < 2) for i, s in enumerate(styles))}</ul>
{paragraphs(H['gioi_thieu'])}
<p>Muốn cắt ngay? Xem <a href="{esc(site['trang_dich_vu']['path'])}">dịch vụ cắt tóc layer tại TP.HCM</a> của {esc(site['ten'])}.</p>
{cta_html(site)}
"""
    item_list = {
        "@type": "ItemList",
        "name": H["h1"],
        "itemListElement": [
            {"@type": "ListItem", "position": i, "url": site["domain"] + s["path"], "name": s["ten"]}
            for i, s in enumerate(styles, 1)
        ],
    }
    first = next((s["images"][0]["src"] for s in styles if s["images"]), None)
    write(path, page(site, path=path, title=H["title"], desc=H["meta_description"], crumbs=crumbs,
                     main=main, schema=base_schema(site) + [item_list], og_image=first))
    return {"url": path, "title": H["title"], "desc": H["meta_description"], "h1": H["h1"],
            "keyword": H["tu_khoa_chinh"], "images": [s["images"][0] for s in styles if s["images"]]}


def build_style(site, style, by_slug):
    H = site["trang_kieu_toc"]
    path = style["path"]
    crumbs = [("Trang chủ", "/"), (H["breadcrumb"], H["path"]), (style["ten"], path)]
    imgs = style["images"]
    hero = f'<div class="hero">{img_tag(imgs[0], eager=True, sizes="(max-width: 960px) 100vw, 928px")}</div>' if imgs else ""
    related = [by_slug[s] for s in style.get("lien_quan", []) if s in by_slug]
    rel_html = ('<h2>Kiểu tóc layer khác</h2><ul class="related">'
                + "".join(f'<li><a href="{esc(r["path"])}">{esc(r["ten"])}</a></li>' for r in related)
                + "</ul>") if related else ""
    sections = "".join(f"<h2>{esc(sec['h2'])}</h2>{paragraphs(sec.get('doan', []))}{bullets(sec.get('y', []))}"
                       for sec in style["noi_dung"])
    landing = site["trang_dich_vu"]
    main = f"""
<h1>{esc(style['h1'])}</h1>
<p class="lead">{esc(style['tom_tat'])}</p>
{hero}
{paragraphs(style['gioi_thieu'])}
{('<h2>Mẫu ' + esc(style['ten'].lower()) + ' cắt tại ' + esc(site['ten']) + '</h2>' + gallery(imgs[1:])) if len(imgs) > 1 else ''}
{sections}
{cta_html(site, f"Muốn thử {style['ten'].lower()}? Gửi ảnh tóc hiện tại qua Zalo để stylist tư vấn có hợp khuôn mặt bạn không.")}
{faq_html(style.get('faq', []))}
<p>Xem thêm: <a href="{esc(landing['path'])}">cắt tóc layer tại TP.HCM</a> · <a href="{esc(H['path'])}">tất cả kiểu tóc layer</a></p>
{rel_html}
"""
    webpage = {
        "@type": "WebPage",
        "name": style["title"],
        "url": site["domain"] + path,
        "description": style["meta_description"],
        "inLanguage": "vi",
        "about": {"@id": site["domain"] + path + "#dich-vu"},
        "isPartOf": {"@id": site["domain"] + "/#website"},
    }
    service = {
        "@type": "Service",
        "@id": site["domain"] + path + "#dich-vu",
        "name": f"{style['ten']} tại {site['ten']}",
        "serviceType": "Cắt tóc layer",
        "areaServed": {"@type": "City", "name": "Thành phố Hồ Chí Minh"},
        "provider": [{"@id": f"{site['domain']}/#{b['id']}"} for b in site["chi_nhanh"]
                     if b["thanh_pho"] == site["thanh_pho_chinh"]],
    }
    if imgs:
        webpage["primaryImageOfPage"] = site["domain"] + imgs[0]["src"]
        webpage["image"] = [
            {"@type": "ImageObject", "contentUrl": site["domain"] + im["src"], "caption": im["alt"],
             **({"width": im["w"], "height": im["h"]} if im.get("w") else {})}
            for im in imgs
        ]
    schema = base_schema(site) + [webpage, service]
    if style.get("faq"):
        schema.append(faq_schema(style["faq"]))
    write(path, page(site, path=path, title=style["title"], desc=style["meta_description"], crumbs=crumbs,
                     main=main, schema=schema, og_image=imgs[0]["src"] if imgs else None))
    return {"url": path, "title": style["title"], "desc": style["meta_description"], "h1": style["h1"],
            "keyword": style["tu_khoa_chinh"], "images": imgs}


# ---------------------------------------------------------------- kiểm tra + xuất


def check(site, styles):
    slugs = [s["slug"] for s in styles]
    for s in {x for x in slugs if slugs.count(x) > 1}:
        warn(f"Trùng slug: {s}")
    for s in styles:
        if s["slug"] != slugify(s["slug"]):
            warn(f"Slug '{s['slug']}' nên viết không dấu, chữ thường, nối bằng '-': {slugify(s['slug'])}")
        for bad in set(s.get("lien_quan", [])) - set(slugs):
            warn(f"{s['slug']}: lien_quan trỏ tới kiểu không tồn tại '{bad}'")
    pages = [site["trang_dich_vu"], site["trang_kieu_toc"]] + styles
    titles = [p["title"] for p in pages]
    for p in pages:
        name = p.get("slug") or p["path"]
        if len(p["title"]) > 60:
            warn(f"{name}: title dài {len(p['title'])} ký tự (nên ≤ 60, Google sẽ cắt bớt)")
        if not 110 <= len(p["meta_description"]) <= 160:
            warn(f"{name}: meta description dài {len(p['meta_description'])} ký tự (nên 110–160)")
        if titles.count(p["title"]) > 1:
            warn(f"{name}: title bị trùng với trang khác")
        if p["tu_khoa_chinh"].lower() not in (p["title"] + " " + p["h1"]).lower():
            warn(f"{name}: từ khoá chính '{p['tu_khoa_chinh']}' không có trong title/H1")
    for b in site["chi_nhanh"]:
        for field in ("dia_chi", "thanh_pho"):
            if not b.get(field):
                warn(f"Chi nhánh {b['id']}: thiếu {field}")
    if not (site["dat_lich"]["zalo"] or site["dat_lich"]["dien_thoai"]):
        warn("Chưa có số Zalo/điện thoại đặt lịch")


def write_sitemap(site, pages):
    today = date.today().isoformat()
    urls = []
    for p in pages:
        imgs = "".join(
            f"<image:image><image:loc>{esc(site['domain'] + im['src'])}</image:loc></image:image>"
            for im in p["images"][:30]
        )
        urls.append(f"<url><loc>{esc(site['domain'] + p['url'])}</loc><lastmod>{today}</lastmod>{imgs}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    (DIST / "sitemap-toc-layer.xml").write_text(xml, encoding="utf-8")


def write_seo_map(site, pages):
    with open(DIST / "seo-map.csv", "w", newline="", encoding="utf-8-sig") as f:  # mở được bằng Excel
        w = csv.writer(f)
        w.writerow(["URL", "Từ khoá chính", "Title", "Số ký tự title", "Meta description", "Số ký tự meta", "H1", "Số ảnh"])
        for p in pages:
            w.writerow([site["domain"] + p["url"], p["keyword"], p["title"], len(p["title"]), p["desc"],
                        len(p["desc"]), p["h1"], len(p["images"])])


def main():
    site = load_json("site.json")
    styles = [s for s in load_json("styles.json") if s.get("xuat_ban", True)]
    check(site, styles)
    if Image is None:
        warn("Chưa cài Pillow nên ảnh chỉ được đổi tên, không nén WebP: pip install pillow")
    if DIST.exists():
        # giữ lại ảnh đã nén để lần chạy sau nhanh hơn, xoá phần còn lại
        for p in DIST.iterdir():
            if p.name != "anh":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    DIST.mkdir(exist_ok=True)

    hub_path = site["trang_kieu_toc"]["path"]
    for s in styles:
        s["path"] = f"{hub_path}{s['slug']}/"
        s["images"] = process_images(s["slug"], f"toc-{s['slug']}-chan-hair", f"{s['ten']} tại {site['ten']}")
        if len(s["images"]) < 4:
            warn(f"{s['slug']}: mới có {len(s['images'])} ảnh — nên có ít nhất 4–6 ảnh thật trước khi đăng (thư mục anh/{s['slug']}/)")
    landing_imgs = process_images(LANDING_IMG_DIR, "cat-toc-layer-tphcm-chan-hair",
                                  f"Cắt tóc layer tại {site['ten']} TP.HCM")
    by_slug = {s["slug"]: s for s in styles}

    pages = [build_landing(site, styles, landing_imgs), build_hub(site, styles)]
    pages += [build_style(site, s, by_slug) for s in styles]
    write_sitemap(site, pages)
    write_seo_map(site, pages)

    print(f"Đã tạo {len(pages)} trang trong {DIST.relative_to(ROOT)}/:")
    for p in pages:
        print(f"  {site['domain']}{p['url']}  ({len(p['images'])} ảnh)")
    if warnings:
        print(f"\n{len(warnings)} lưu ý:")
        for w in warnings:
            print("  - " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
