# Hướng dẫn đưa trang "cắt tóc layer" lên chanhair.vn

Bạn nhận được 3 file:
- `chanhair-seo-trang-web.zip`: **13 trang** sẵn sàng đăng, gồm 1 trang dịch vụ chính, 1 trang tổng hợp và 11 trang kiểu tóc.
- `seo-map.csv`: bảng URL, title và mô tả SEO của từng trang, mở bằng Excel. File này chỉ để tra cứu, **không** tải lên web.
- File hướng dẫn này.

Giải nén file zip sẽ thấy các thư mục trùng với đường dẫn trên web:

```
cat-toc-layer-ho-chi-minh/index.html   →  chanhair.vn/cat-toc-layer-ho-chi-minh/
toc-layer/index.html                   →  chanhair.vn/toc-layer/
toc-layer/wolf-cut/index.html          →  chanhair.vn/toc-layer/wolf-cut/
...
anh/                                   →  ảnh (khi đã có ảnh)
sitemap-toc-layer.xml                  →  chanhair.vn/sitemap-toc-layer.xml
```

**Bước 1: xem chanhair.vn đang làm bằng gì.** Đăng nhập trang quản trị, rồi làm theo đúng mục bên dưới:

- **Mục A:** có hosting với cPanel, DirectAdmin, File Manager hoặc FTP. Đây là cách dễ nhất, áp dụng được cả khi web chạy WordPress.
- **Mục B:** chỉ có WordPress, không vào được hosting.
- **Mục C:** web làm bằng LadiPage.

---

## A. Hosting có File Manager / FTP (khoảng 5 phút)

1. Đăng nhập cPanel, mở **File Manager**, vào thư mục gốc của web. Thư mục này thường là `public_html` và có sẵn file `index.html` hoặc `wp-config.php`.
2. Bấm **Upload**, tải file `chanhair-seo-trang-web.zip` lên đúng thư mục đó.
3. Chuột phải vào file zip, chọn **Extract**, giải nén ngay tại thư mục gốc.
4. Xoá file zip vừa tải lên. Sau khi giải nén, file này không cần nằm trên web nữa.
5. Mở thử `https://chanhair.vn/cat-toc-layer-ho-chi-minh/`. Thấy trang hiện ra là xong.

Cách này không đụng tới trang chủ hiện tại. Nếu web chạy WordPress, WordPress vẫn hoạt động bình thường, vì máy chủ ưu tiên thư mục có thật trước các trang của WordPress.

## B. Chỉ có WordPress (khoảng 10 phút mỗi trang)

Làm lần lượt cho từng trang trong `seo-map.csv`:

1. Vào **Trang → Thêm mới**.
2. Đặt **tiêu đề** theo cột H1 trong `seo-map.csv`.
3. Thêm khối **HTML tuỳ chỉnh** (Custom HTML).
4. Mở file `index.html` của trang đó bằng Notepad. Chép đoạn từ `<main` đến `</main>` dán vào khối HTML.
5. Ở ô **Đường dẫn tĩnh** (permalink / slug), điền đúng đuôi URL, ví dụ `cat-toc-layer-ho-chi-minh`.
   - Riêng các trang kiểu tóc, phải chọn **Trang cha** là trang "Kiểu tóc layer" (`toc-layer`). Như vậy đường dẫn mới thành `/toc-layer/wolf-cut/`.
6. Nếu có plugin Rank Math hoặc Yoast, chép cột **Title** và **Meta description** trong `seo-map.csv` vào ô SEO của trang.
7. Bấm **Đăng**.

## C. LadiPage

LadiPage không cho tải nguyên thư mục lên, nên phải tạo từng trang:

1. Tạo **Landing page mới** (trang trắng) cho mỗi URL.
2. Trong **Cài đặt trang → SEO & Social**, dán Title và Meta description từ `seo-map.csv`.
3. Ở bước **Xuất bản**, chọn tên miền chanhair.vn và điền đường dẫn, ví dụ `cat-toc-layer-ho-chi-minh`.
4. Nội dung có thể dựng lại bằng các khối chữ và ảnh của LadiPage, theo đúng thứ tự trong file `index.html`, mở bằng trình duyệt để xem.

Nếu web dùng LadiPage, báo lại để mình làm bản riêng cho dễ dán hơn.

---

## Sau khi đăng: 3 việc bắt buộc

1. **Gắn link vào trang chủ hoặc menu** chanhair.vn: một nút "Cắt tóc layer" trỏ tới `/cat-toc-layer-ho-chi-minh/` và một nút "Kiểu tóc layer" trỏ tới `/toc-layer/`. Trang không có link trỏ vào thì Google rất lâu mới tìm thấy.
2. **Google Search Console** (search.google.com/search-console):
   - Thêm chanhair.vn rồi xác minh.
   - Vào **Sơ đồ trang web**, nộp `sitemap-toc-layer.xml` (cách A), hoặc sitemap của WordPress/LadiPage (cách B, C).
   - Dán từng URL vào ô **Kiểm tra URL** trên cùng, bấm **Yêu cầu lập chỉ mục**.
3. **Google Maps (Google Business Profile)** của 2 salon: thêm dịch vụ "Cắt tóc layer" và gắn link tới trang vừa đăng.

## Khi có ảnh mới

Gửi ảnh cho Claude, ghi rõ ảnh nào là kiểu gì. Claude sẽ tạo lại bộ trang. Bạn chỉ cần tải file zip mới lên và giải nén đè như cách A.
