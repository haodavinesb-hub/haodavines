# Chan Hair: trang SEO "cắt tóc layer TP.HCM"

Bộ công cụ này tạo các trang chuẩn SEO cho chanhair.vn. Mục tiêu là khách tìm **"cắt tóc layer ở Hồ Chí Minh"**, **"tóc layer ngắn"**, **"wolf cut"**… trên Google thì thấy Chan Hair.

Bạn chỉ cần làm hai việc: **bỏ ảnh vào đúng thư mục** rồi **chạy một lệnh**. Script sẽ tự đổi tên ảnh cho chuẩn SEO, nén ảnh, viết alt, gắn schema cho Google, tạo sitemap và làm sẵn trang để đưa lên web.

## 1. Cấu trúc đường dẫn (URL)

```
chanhair.vn/cat-toc-layer-ho-chi-minh/      ← trang dịch vụ chính
chanhair.vn/toc-layer/                       ← tổng hợp các kiểu tóc layer
chanhair.vn/toc-layer/<kiểu>/                ← mỗi kiểu tóc một trang
```

| Đường dẫn | Từ khoá chính | Từ khoá phụ (đã có trong nội dung) |
|---|---|---|
| `/cat-toc-layer-ho-chi-minh/` | cắt tóc layer nữ TP.HCM | cắt tóc layer tphcm, hồ chí minh, sài gòn, quận 10, bình thạnh, cắt tóc layer bao nhiêu tiền |
| `/toc-layer/` | kiểu tóc layer nữ đẹp 2026 | các kiểu tóc layer, tóc tầng |
| `/toc-layer/layer-dai/` | tóc layer dài | layer dài hàn quốc, layer dài uốn đuôi |
| `/toc-layer/layer-ngang-vai/` | tóc layer ngang vai | tóc lỡ layer, layer ngang vai uốn cụp |
| `/toc-layer/layer-ngan/` | tóc layer ngắn | bob layer, layer ngắn mặt tròn |
| `/toc-layer/layer-mai-bay/` | tóc layer mái bay | mái thưa hàn quốc, mái rèm, curtain bangs |
| `/toc-layer/layer-uon/` | tóc layer uốn | uốn cụp, uốn sóng lơi, cắt layer và uốn |
| `/toc-layer/butterfly-cut/` | butterfly cut | tóc bướm, layer bướm |
| `/toc-layer/hush-cut/` | hush cut | tóc layer hàn quốc |
| `/toc-layer/wolf-cut/` | wolf cut | wolf cut nữ, octopus cut |
| `/toc-layer/layer-mat-tron/` | tóc layer cho mặt tròn | kiểu tóc layer mặt tròn |
| `/toc-layer/layer-toc-mong/` | tóc mỏng có nên cắt layer | layer cho tóc mỏng, tóc dày |
| `/toc-layer/hime-cut/` | hime cut | tóc hime, hime layer |

Đường dẫn được đặt theo các quy tắc sau:
- Viết không dấu, chữ thường, các từ nối bằng dấu `-`. Đây là cách Google đọc tốt nhất.
- Mỗi trang nhắm **một** từ khoá chính, để các trang không tranh từ khoá của nhau.
- Trang dịch vụ chính nhắm khách *muốn đi cắt*, nên có địa chỉ, giờ mở cửa, nút đặt lịch.
- Trang từng kiểu nhắm khách *đang tìm mẫu*. Trang nào cũng có link về trang dịch vụ chính để dồn sức mạnh SEO về đó.

Danh sách đầy đủ từng trang (URL, từ khoá, title, meta, số ảnh) nằm trong `dist/seo-map.csv`, mở được bằng Excel hoặc Google Sheets.

## 2. Thêm ảnh: phần quan trọng nhất

Mỗi kiểu tóc có một thư mục ảnh riêng, tên thư mục trùng với đuôi URL:

| Thư mục | Trang |
|---|---|
| `anh/cat-toc-layer/` | Ảnh cho trang dịch vụ chính (ảnh salon, stylist đang cắt, before/after) |
| `anh/layer-ngan/` | chanhair.vn/toc-layer/layer-ngan/ |
| `anh/wolf-cut/` | chanhair.vn/toc-layer/wolf-cut/ |
| … | (tên thư mục = `slug` trong `data/styles.json`) |

Cách làm:
1. Chép ảnh vào thư mục. Tên file gốc để nguyên cũng được (IMG_1234.jpg), script sẽ tự đổi thành `toc-layer-ngan-chan-hair-1.webp`.
2. Ảnh được sắp xếp theo tên file. **Ảnh đầu tiên là ảnh bìa** của trang, hiện trên Google và Facebook khi chia sẻ.
3. Muốn mô tả riêng cho ảnh (rất tốt cho Google Hình ảnh), tạo file `_mo-ta.txt` trong thư mục đó, mỗi dòng một ảnh:
   ```
   IMG_1234.jpg: layer ngắn uốn cụp, màu nâu lạnh
   IMG_1240.jpg: before/after tóc dày được tỉa tầng nhẹ
   ```
   Ảnh không có mô tả sẽ có alt tự động, ví dụ "Tóc layer ngắn tại Chan Hair - mẫu 3".

Ảnh thế nào thì tốt cho SEO:
- **Ảnh thật của khách tại salon.** Google ưu tiên ảnh gốc hơn ảnh lấy trên mạng; ảnh lấy trên mạng còn có thể bị khiếu nại bản quyền.
- Mỗi kiểu nên có **ít nhất 6 ảnh**. Script sẽ cảnh báo kiểu nào còn dưới 4 ảnh.
- Ưu tiên ảnh dọc (3:4), đủ sáng, thấy rõ các tầng tóc: chụp nghiêng, chụp sau lưng, ảnh before/after.
- Ảnh từ iPhone (HEIC) cần cài thêm `pip install pillow-heif`, hoặc xuất ảnh sang JPG trước khi chép vào.
- Script tự xoá thông tin GPS và EXIF của ảnh khi nén, nên vị trí chụp hay thông tin máy của khách không bị lộ.

## 3. Thêm hoặc sửa kiểu tóc

Toàn bộ nội dung chữ nằm trong `data/styles.json`. Mỗi kiểu là một khối như sau:

```json
{
  "slug": "layer-ngan",                 ← đuôi URL, không dấu
  "ten": "Tóc layer ngắn",
  "tu_khoa_chinh": "tóc layer ngắn",    ← phải có trong title hoặc h1
  "title": "...",                       ← ≤ 60 ký tự, hiện trên Google
  "meta_description": "...",            ← 110–160 ký tự, đoạn mô tả dưới tiêu đề trên Google
  "h1": "...",
  "tom_tat": "...",                     ← 1–2 câu, hiện trên thẻ kiểu tóc
  "gioi_thieu": ["đoạn 1", "đoạn 2"],
  "noi_dung": [{"h2": "Tiêu đề mục", "doan": ["đoạn..."], "y": ["gạch đầu dòng..."]}],
  "faq": [{"q": "Câu hỏi?", "a": "Trả lời."}],
  "lien_quan": ["wolf-cut", "hush-cut"], ← các kiểu gợi ý ở cuối trang
  "xuat_ban": false                     ← (tuỳ chọn) ẩn kiểu này khi chưa đủ ảnh
}
```

Muốn thêm kiểu mới, chép một khối có sẵn, đổi `slug` và nội dung, rồi tạo thư mục `anh/<slug>/`.

Thông tin salon (chi nhánh, giờ mở cửa, số điện thoại, Zalo, bảng giá, câu hỏi thường gặp của trang chính) nằm trong `data/site.json`.

## 4. Tạo trang

```bash
pip install pillow          # chỉ cần cài một lần
python3 build.py            # tạo lại toàn bộ trang trong dist/
python3 -m http.server -d dist 8000
# mở http://localhost:8000/cat-toc-layer-ho-chi-minh/ để xem thử
```

Mỗi lần chạy, script kiểm tra và báo các lỗi SEO thường gặp:
- title quá dài,
- meta description quá ngắn hoặc quá dài,
- trùng title giữa các trang,
- thiếu từ khoá chính trong title/H1,
- kiểu tóc còn ít ảnh.

Kết quả trong `dist/`:
- `cat-toc-layer-ho-chi-minh/index.html`, `toc-layer/.../index.html`: các trang hoàn chỉnh. Mỗi trang có title, meta description, canonical, Open Graph, schema JSON-LD (HairSalon, Service, BreadcrumbList, FAQPage, ImageObject), breadcrumb, nút đặt lịch Zalo/gọi điện và thanh đặt lịch cố định trên điện thoại.
- `anh/toc-layer/...`: ảnh đã nén WebP, có hai cỡ (1200px và 600px) để điện thoại tải nhanh.
- `sitemap-toc-layer.xml`: sitemap có kèm ảnh, dùng để nộp cho Google.
- `seo-map.csv`: bảng tổng hợp toàn bộ URL, title và meta.

## 5. Đưa lên chanhair.vn

Thư mục `dist/` có cấu trúc **giống hệt đường dẫn trên web**:
- **Nếu chanhair.vn là hosting thường hoặc có quyền FTP/cPanel**, tải toàn bộ nội dung `dist/` lên thư mục gốc của website, giữ nguyên cấu trúc thư mục. Trang chủ hiện tại không bị ảnh hưởng.
- **Nếu dùng WordPress**, tạo Page với đường dẫn tĩnh (slug) đúng như bảng ở mục 1. Dán nội dung, title và meta description từ `seo-map.csv` vào Rank Math hoặc Yoast. Tải ảnh trong `dist/anh/` lên Thư viện kèm alt text.
- **Nếu dùng LadiPage**, mỗi trang là một landing page riêng, gắn vào tên miền chanhair.vn với đường dẫn tương ứng. Schema dán vào phần "Mã HTML/Javascript" trong cài đặt trang.

Sau khi đăng, nhớ thêm link "Cắt tóc layer" vào menu hoặc trang chủ chanhair.vn. Trang không có link trỏ vào thì Google rất chậm tìm thấy.

## 6. Việc cần làm ngoài website để lên top

Từ khoá có chữ **"ở Hồ Chí Minh"**, **"quận 10"**, **"gần đây"** là tìm kiếm địa phương. Với loại này, Google hiển thị **khung bản đồ (Google Maps)** trước cả kết quả website, nên phải làm song song cả hai.

**Google Business Profile** (hồ sơ Google Maps của từng chi nhánh):
1. Mục *Dịch vụ*: thêm "Cắt tóc layer", "Cắt tóc butterfly", "Wolf cut"…, mỗi dịch vụ có mô tả ngắn và link tới trang tương ứng.
2. Đăng ảnh layer mới mỗi tuần, dùng chính những ảnh đã đăng lên web.
3. Khi xin khách đánh giá, gợi ý khách viết rõ dịch vụ, ví dụ "cắt layer ở đây rất đẹp". Từ khoá trong đánh giá giúp lên khung bản đồ.
4. Dùng Google Posts (bài đăng trên hồ sơ) giới thiệu từng kiểu layer, kèm nút "Tìm hiểu thêm" trỏ về trang web.
5. Tên, địa chỉ, số điện thoại trên Maps phải **giống hệt** trên website, kể cả tên phường mới sau sáp nhập.

**Google Search Console** (miễn phí, cần quyền quản trị tên miền):
1. Xác minh chanhair.vn.
2. Nộp `https://chanhair.vn/sitemap-toc-layer.xml` ở mục *Sơ đồ trang web*.
3. Dùng *Kiểm tra URL* → *Yêu cầu lập chỉ mục* cho từng trang mới.
4. Sau 4–8 tuần, xem mục *Hiệu suất* để biết khách đang tìm từ khoá nào và trang nào đang lên.

**Mạng xã hội và backlink:**
- Bio Instagram (@chan_hairsalon), TikTok (@chanhair401) và Facebook từng chi nhánh: để link `chanhair.vn/toc-layer/`.
- Mỗi video hoặc ảnh layer đăng lên mạng xã hội: caption ghi tên kiểu ("wolf cut", "layer ngắn"), địa chỉ salon và link trang kiểu đó.
- Trong hợp đồng hợp tác với KOL/KOC, xin họ gắn link trang kiểu tóc họ làm.
- Từ khoá cấp thành phố như "cắt tóc layer tphcm" hiện do các trang top list chiếm gần hết top 10, nên **được nhắc tên trong các bài đó** cũng quan trọng như tự lên top. Liên hệ các trang đang xếp hạng để xin đưa Chan Hair vào bài, kèm địa chỉ mới và link trang dịch vụ:
  - Bài "cắt tóc layer TP.HCM": toplist.vn, mytour.vn, hcmtoplist.com, topwat.com, bloganchoi.com, timan.vn.
  - Bài "làm tóc Quận 10": sheis.vn, 1900hairsalon.com, nhacahairsalon.com (bài này đã có Chan Hair).
- Chưa có bài top list nào riêng về **"cắt tóc layer quận 10"** hay **"cắt tóc layer bình thạnh"**. Đây là chỗ trống dễ chiếm nhất, và trang dịch vụ đã có sẵn hai từ khoá này.

**Nhịp đăng gợi ý:**
- Mỗi tuần bổ sung ảnh cho 1–2 kiểu, chạy lại `build.py`, rồi tải lên.
- Trang được cập nhật đều đặn và có nhiều ảnh thật sẽ lên hạng nhanh hơn trang để im.
- Thường cần **2–4 tháng** để thấy kết quả ổn định trên Google.

## 7. Thông tin cần xác nhận lại

Những thông tin dưới đây được tổng hợp từ nguồn công khai trên mạng, có thể đã cũ. Hãy kiểm tra lại trong `data/site.json`:

- [ ] Hotline 0963 834 909 và Zalo 0824 599 999 còn đúng không.
- [ ] Giờ mở cửa 8:30 – 20:00 của từng chi nhánh.
- [ ] Địa chỉ theo tên phường mới: 401 Sư Vạn Hạnh → Phường Hòa Hưng; 64 D5 → Phường Thạnh Mỹ Tây. Cần khớp với Google Maps.
- [ ] Địa chỉ chi nhánh Đà Nẵng. Chưa tìm thấy trên mạng nên chưa đưa vào.
- [ ] Link Google Maps của từng chi nhánh (trường `google_maps`).
- [ ] Bảng giá cắt layer (trường `bang_gia`). Hiện trang ghi "báo giá sau khi tư vấn".
  - Các salon đang lên top đều ghi giá rõ, ví dụ "layer cơ bản từ 200k, butterfly/wolf cut từ 400k, đã gồm gội sấy". Có bảng giá sẽ dễ lên từ khoá "cắt tóc layer bao nhiêu tiền" hơn.
  - Các con số đang có trên mạng về Chan Hair không khớp nhau: trang chanhair.vn ghi giá trị cắt/thiết kế 200k, toplist ghi 150k–500k, nhacahairsalon ghi "từ 80.000đ".
- [ ] Các cam kết "giá công khai, không phát sinh phụ phí, không ép dịch vụ" (lấy từ trang chủ chanhair.vn) có còn áp dụng không. Nếu salon có bảo hành cắt lại miễn phí, nên ghi rõ số ngày.
- [ ] 401 Sư Vạn Hạnh có gần Vạn Hạnh Mall không. Nếu gần, thêm một câu vào trang dịch vụ, vì nhiều người tìm "cắt tóc nữ gần Vạn Hạnh Mall".
- [ ] Các ý trong mục "Vì sao nên cắt tóc layer tại Chan Hair" (trường `ly_do`) có đúng với cách salon đang làm không.
